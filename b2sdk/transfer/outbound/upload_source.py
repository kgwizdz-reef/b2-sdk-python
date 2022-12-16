######################################################################
#
# File: b2sdk/transfer/outbound/upload_source.py
#
# Copyright 2020 Backblaze Inc. All Rights Reserved.
#
# License https://www.backblaze.com/using_b2_code.html
#
######################################################################

import hashlib
import io
import logging
import os

from abc import abstractmethod
from enum import auto, Enum, unique
from typing import Callable, List, Optional, Union

from b2sdk.exception import InvalidUploadSource
from b2sdk.file_version import FileVersion
from b2sdk.http_constants import DEFAULT_MIN_PART_SIZE
from b2sdk.stream.range import RangeOfInputStream, wrap_with_range
from b2sdk.transfer.outbound.copy_source import CopySource
from b2sdk.transfer.outbound.outbound_source import OutboundTransferSource
from b2sdk.utils import hex_sha1_of_unlimited_stream, Sha1HexDigest, update_digest_from_stream

logger = logging.getLogger(__name__)


@unique
class UploadMode(Enum):
    """ Mode of file uploads """
    FULL = auto()  #: always upload the whole file
    INCREMENTAL = auto()  #: use incremental uploads when possible


class AbstractUploadSource(OutboundTransferSource):
    """
    The source of data for uploading to b2.
    """

    @abstractmethod
    def get_content_sha1(self) -> Optional[Sha1HexDigest]:
        """
        Returns a 40-character string containing the hex SHA1 checksum of the data in the file.
        """

    @abstractmethod
    def open(self) -> io.IOBase:
        """
        Returns a binary file-like object from which the data can be read.
        """

    def is_upload(self) -> bool:
        return True

    def is_copy(self) -> bool:
        return False

    def is_sha1_known(self) -> bool:
        """
        Returns information whether SHA1 of the source is currently available.
        Note that negative result doesn't mean that SHA1 is not available.
        Calling ``get_content_sha1`` can still provide a valid digest.
        """
        return False


class UploadSourceBytes(AbstractUploadSource):
    def __init__(
        self,
        data_bytes: Union[bytes, bytearray],
        content_sha1: Optional[Sha1HexDigest] = None,
    ):
        """
        Initialize upload source using given bytes.

        :param data_bytes: Data that is to be uploaded.
        :param content_sha1: SHA1 hexdigest of the data, or ``None``.
        """
        self.data_bytes = data_bytes
        self.content_sha1 = content_sha1

    def __repr__(self) -> str:
        return '<{classname} data={data} id={id}>'.format(
            classname=self.__class__.__name__,
            data=str(self.data_bytes[:20]) +
            '...' if len(self.data_bytes) > 20 else self.data_bytes,
            id=id(self),
        )

    def get_content_length(self) -> int:
        return len(self.data_bytes)

    def get_content_sha1(self) -> Optional[Sha1HexDigest]:
        if self.content_sha1 is None:
            self.content_sha1 = hashlib.sha1(self.data_bytes).hexdigest()
        return self.content_sha1

    def open(self):
        return io.BytesIO(self.data_bytes)

    def is_sha1_known(self) -> bool:
        return self.content_sha1 is not None


class UploadSourceLocalFileBase(AbstractUploadSource):
    def __init__(
        self,
        local_path: Union[os.PathLike, str],
        content_sha1: Optional[Sha1HexDigest] = None,
    ):
        """
        Initialize upload source using provided path.

        :param local_path: Any path-like object that points to a file to be uploaded.
        :param content_sha1: SHA1 hexdigest of the data, or ``None``.
        """
        self.local_path = local_path
        self.content_length = 0
        self.content_sha1 = content_sha1
        self.digest = None
        self.digest_progress = 0
        self.check_path_and_get_size()

    def check_path_and_get_size(self) -> None:
        if not os.path.isfile(self.local_path):
            raise InvalidUploadSource(self.local_path)
        self.content_length = os.path.getsize(self.local_path)

    def __repr__(self) -> str:
        return (
            '<{classname} local_path={local_path} content_length={content_length} '
            'content_sha1={content_sha1} id={id}>'
        ).format(
            classname=self.__class__.__name__,
            local_path=self.local_path,
            content_length=self.content_length,
            content_sha1=self.content_sha1,
            id=id(self),
        )

    def get_content_length(self) -> int:
        return self.content_length

    def _get_hexdigest(self, length: int = 0) -> Sha1HexDigest:
        length = length or self.content_length

        if self.digest is None:
            self.digest = hashlib.sha1()
            self.digest_progress = 0

        if length < self.digest_progress:
            raise ValueError("Length value can not decrease between calls")

        if length > self.digest_progress:
            with self.open() as fp:
                range_length = length - self.digest_progress
                range_ = wrap_with_range(
                    fp, self.content_length, self.digest_progress, range_length
                )
                update_digest_from_stream(self.digest, range_, range_length)
            self.digest_progress = length

        return Sha1HexDigest(self.digest.hexdigest())

    def get_content_sha1(self) -> Optional[Sha1HexDigest]:
        if self.content_sha1 is None:
            self.content_sha1 = self._get_hexdigest()
        return self.content_sha1

    def open(self):
        return io.open(self.local_path, 'rb')

    def is_sha1_known(self) -> bool:
        return self.content_sha1 is not None


class UploadSourceLocalFileRange(UploadSourceLocalFileBase):
    def __init__(
        self,
        local_path: Union[os.PathLike, str],
        content_sha1: Optional[Sha1HexDigest] = None,
        offset: int = 0,
        length: Optional[int] = None,
    ):
        """
        Initialize upload source using provided path.

        :param local_path: Any path-like object that points to a file to be uploaded.
        :param content_sha1: SHA1 hexdigest of the data, or ``None``.
        :param offset: Position in the file where upload should start from.
        :param length: Amount of data to be uploaded. If ``None``, length of
                      the remainder of the file is taken.
        """
        super().__init__(local_path, content_sha1)
        self.file_size = self.content_length
        self.offset = offset
        if length is None:
            self.content_length = self.file_size - self.offset
        else:
            if length + self.offset > self.file_size:
                raise ValueError('Range length overflow file size')
            self.content_length = length

    def __repr__(self) -> str:
        return (
            '<{classname} local_path={local_path} offset={offset} '
            'content_length={content_length} content_sha1={content_sha1} id={id}>'
        ).format(
            classname=self.__class__.__name__,
            local_path=self.local_path,
            offset=self.offset,
            content_length=self.content_length,
            content_sha1=self.content_sha1,
            id=id(self),
        )

    def open(self):
        fp = super(UploadSourceLocalFileRange, self).open()
        return wrap_with_range(fp, self.file_size, self.offset, self.content_length)


class UploadSourceLocalFile(UploadSourceLocalFileBase):
    def get_incremental_sources(
        self,
        file_version: FileVersion,
        min_part_size: Optional[int] = None,
    ) -> List[OutboundTransferSource]:
        """
        Split the upload into a copy and upload source constructing an incremental upload

        This will return a list of upload sources.  If the upload cannot split, the method will return [self].
        """

        if not file_version:
            logger.debug(
                "Fallback to full upload for %s -- no matching file on server", self.local_path
            )
            return [self]

        min_part_size = min_part_size or DEFAULT_MIN_PART_SIZE
        if file_version.size < min_part_size:
            # existing file size below minimal large file part size
            logger.debug(
                "Fallback to full upload for %s -- remote file is smaller than %i bytes",
                self.local_path, min_part_size
            )
            return [self]

        if self.get_content_length() < file_version.size:
            logger.debug(
                "Fallback to full upload for %s -- local file is smaller than remote",
                self.local_path
            )
            return [self]

        content_sha1 = file_version.get_content_sha1()

        if not content_sha1:
            logger.debug(
                "Fallback to full upload for %s -- remote file content SHA1 unknown",
                self.local_path
            )
            return [self]

        if self._get_hexdigest(file_version.size) != content_sha1:
            logger.debug(
                "Fallback to full upload for %s -- content in common range differs", self.local_path
            )
            return [self]

        logger.debug("Incremental upload of %s is possible.", self.local_path)

        if file_version.server_side_encryption and file_version.server_side_encryption.is_unknown():
            source_encryption = None
        else:
            source_encryption = file_version.server_side_encryption

        sources = [
            CopySource(
                file_version.id_,
                offset=0,
                length=file_version.size,
                encryption=source_encryption,
                source_file_info=file_version.file_info,
                source_content_type=file_version.content_type,
            ),
            UploadSourceLocalFileRange(self.local_path, offset=file_version.size),
        ]
        return sources


class UploadSourceStream(AbstractUploadSource):
    def __init__(
        self,
        stream_opener: Callable[[], io.IOBase],
        stream_length: Optional[int] = None,
        stream_sha1: Optional[Sha1HexDigest] = None,
    ):
        """
        Initialize upload source using arbitrary function.

        :param stream_opener: A function that opens a stream for uploading.
        :param stream_length: Length of the stream. If ``None``, data will be calculated
                      from the stream the first time it's required.
        :param stream_sha1: SHA1 of the stream. If ``None``, data will be calculated from
                      the stream the first time it's required.
        """
        self.stream_opener = stream_opener
        self._content_length = stream_length
        self._content_sha1 = stream_sha1

    def __repr__(self) -> str:
        return (
            '<{classname} stream_opener={stream_opener} content_length={content_length} '
            'content_sha1={content_sha1} id={id}>'
        ).format(
            classname=self.__class__.__name__,
            stream_opener=repr(self.stream_opener),
            content_length=self._content_length,
            content_sha1=self._content_sha1,
            id=id(self),
        )

    def get_content_length(self) -> int:
        if self._content_length is None:
            self._set_content_length_and_sha1()
        return self._content_length

    def get_content_sha1(self) -> Optional[Sha1HexDigest]:
        if self._content_sha1 is None:
            self._set_content_length_and_sha1()
        return self._content_sha1

    def open(self):
        return self.stream_opener()

    def _set_content_length_and_sha1(self) -> None:
        sha1, content_length = hex_sha1_of_unlimited_stream(self.open())
        self._content_length = content_length
        self._content_sha1 = sha1

    def is_sha1_known(self) -> bool:
        return self._content_sha1 is not None


class UploadSourceStreamRange(UploadSourceStream):
    def __init__(
        self,
        stream_opener: Callable[[], io.IOBase],
        offset: int = 0,
        stream_length: Optional[int] = None,
        stream_sha1: Optional[Sha1HexDigest] = None,
    ):
        """
        Initialize upload source using arbitrary function.

        :param stream_opener: A function that opens a stream for uploading.
        :param offset: Offset from which stream should be uploaded.
        :param stream_length: Length of the stream. If ``None``, data will be calculated
                      from the stream the first time it's required.
        :param stream_sha1: SHA1 of the stream. If ``None``, data will be calculated from
                      the stream the first time it's required.
        """
        super(UploadSourceStreamRange, self).__init__(
            stream_opener,
            stream_length=stream_length,
            stream_sha1=stream_sha1,
        )
        self._offset = offset

    def __repr__(self) -> str:
        return (
            '<{classname} stream_opener={stream_opener} offset={offset} '
            'content_length={content_length} content_sha1={content_sha1} id={id}>'
        ).format(
            classname=self.__class__.__name__,
            stream_opener=repr(self.stream_opener),
            offset=self._offset,
            content_length=self._content_length,
            content_sha1=self._content_sha1,
            id=id(self),
        )

    def open(self):
        return RangeOfInputStream(
            super(UploadSourceStreamRange, self).open(), self._offset, self._content_length
        )

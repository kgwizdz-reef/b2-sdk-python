######################################################################
#
# File: b2sdk/v1/__init__.py
#
# Copyright 2019 Backblaze Inc. All Rights Reserved.
#
# License https://www.backblaze.com/using_b2_code.html
#
######################################################################

# this file maps the external interface into internal interface
# it will come handy if we ever need to move something


# core

from b2sdk.api import B2Api
from b2sdk.bucket import Bucket
from b2sdk.bucket import BucketFactory
from b2sdk.bucket import LargeFileUploadState
from b2sdk.bucket import PartProgressReporter

assert B2Api
assert Bucket
assert BucketFactory
assert LargeFileUploadState
assert PartProgressReporter

from b2sdk.raw_api import ALL_CAPABILITIES

# account info

from b2sdk.account_info.abstract import AbstractAccountInfo
from b2sdk.account_info.in_memory import InMemoryAccountInfo
from b2sdk.account_info.sqlite_account_info import SqliteAccountInfo
from b2sdk.account_info.upload_url_pool import UrlPoolAccountInfo
from b2sdk.account_info.upload_url_pool import UploadUrlPool

assert AbstractAccountInfo
assert InMemoryAccountInfo
assert SqliteAccountInfo
assert UrlPoolAccountInfo
assert UploadUrlPool

# version & version utils

from b2sdk.version import VERSION, USER_AGENT

assert VERSION
assert USER_AGENT

from b2sdk.version_utils import rename_argument, rename_function
assert rename_argument
assert rename_function

# utils

from b2sdk.utils import b2_url_encode, b2_url_decode, choose_part_ranges, format_and_scale_fraction, format_and_scale_number, hex_sha1_of_stream, hex_sha1_of_bytes, TempDir

assert TempDir
assert b2_url_decode
assert b2_url_encode
assert choose_part_ranges
assert format_and_scale_fraction
assert format_and_scale_number
assert hex_sha1_of_bytes
assert hex_sha1_of_stream

# data classes

from b2sdk.file_version import FileIdAndName
from b2sdk.file_version import FileVersionInfo
from b2sdk.part import Part
from b2sdk.unfinished_large_file import UnfinishedLargeFile

assert FileIdAndName
assert FileVersionInfo
assert Part
assert UnfinishedLargeFile

# progress reporting

from b2sdk.progress import AbstractProgressListener
from b2sdk.progress import DoNothingProgressListener
from b2sdk.progress import ProgressListenerForTest
from b2sdk.progress import SimpleProgressListener
from b2sdk.progress import TqdmProgressListener

assert AbstractProgressListener
assert DoNothingProgressListener
assert ProgressListenerForTest
assert SimpleProgressListener
assert TqdmProgressListener

# raw_simulator

from b2sdk.raw_simulator import BucketSimulator
from b2sdk.raw_simulator import FakeResponse
from b2sdk.raw_simulator import FileSimulator
from b2sdk.raw_simulator import KeySimulator
from b2sdk.raw_simulator import PartSimulator
from b2sdk.raw_simulator import RawSimulator

assert BucketSimulator
assert FakeResponse
assert FileSimulator
assert KeySimulator
assert PartSimulator
assert RawSimulator

# raw_api

from b2sdk.raw_api import AbstractRawApi
from b2sdk.raw_api import B2RawApi

assert AbstractRawApi
assert B2RawApi

# progress

from b2sdk.progress import AbstractStreamWithProgress
from b2sdk.progress import RangeOfInputStream
from b2sdk.progress import ReadingStreamWithProgress
from b2sdk.progress import StreamWithHash
from b2sdk.progress import WritingStreamWithProgress

assert AbstractStreamWithProgress
assert RangeOfInputStream
assert ReadingStreamWithProgress
assert StreamWithHash
assert WritingStreamWithProgress

# source / destination

from b2sdk.download_dest import AbstractDownloadDestination
from b2sdk.download_dest import DownloadDestBytes
from b2sdk.download_dest import DownloadDestLocalFile
from b2sdk.download_dest import DownloadDestProgressWrapper
from b2sdk.download_dest import PreSeekedDownloadDest

assert AbstractDownloadDestination
assert DownloadDestBytes
assert DownloadDestLocalFile
assert DownloadDestProgressWrapper
assert PreSeekedDownloadDest

from b2sdk.upload_source import AbstractUploadSource
from b2sdk.upload_source import UploadSourceBytes
from b2sdk.upload_source import UploadSourceLocalFile

assert AbstractUploadSource
assert UploadSourceBytes
assert UploadSourceLocalFile

# trasferer

from b2sdk.transferer.abstract import AbstractDownloader
from b2sdk.transferer.file_metadata import FileMetadata
from b2sdk.transferer.parallel import AbstractDownloaderThread
from b2sdk.transferer.parallel import FirstPartDownloaderThread
from b2sdk.transferer.parallel import NonHashingDownloaderThread
from b2sdk.transferer.parallel import ParallelDownloader
from b2sdk.transferer.parallel import PartToDownload
from b2sdk.transferer.parallel import WriterThread
from b2sdk.transferer.range import Range
from b2sdk.transferer.simple import SimpleDownloader
from b2sdk.transferer.transferer import Transferer

assert AbstractDownloader
assert AbstractDownloaderThread
assert FileMetadata
assert FirstPartDownloaderThread
assert NonHashingDownloaderThread
assert ParallelDownloader
assert PartToDownload
assert Range
assert SimpleDownloader
assert Transferer
assert WriterThread

# sync

from b2sdk.sync.action import AbstractAction
from b2sdk.sync.action import B2DeleteAction
from b2sdk.sync.action import B2DownloadAction
from b2sdk.sync.action import B2HideAction
from b2sdk.sync.action import B2UploadAction
from b2sdk.sync.action import LocalDeleteAction
from b2sdk.sync.exception import EnvironmentEncodingError
from b2sdk.sync.file import File
from b2sdk.sync.file import FileVersion
from b2sdk.sync.folder import AbstractFolder
from b2sdk.sync.folder import B2Folder
from b2sdk.sync.folder import LocalFolder
from b2sdk.sync.folder_parser import parse_sync_folder
from b2sdk.sync.policy import AbstractFileSyncPolicy
from b2sdk.sync.policy import DownAndDeletePolicy
from b2sdk.sync.policy import DownAndKeepDaysPolicy
from b2sdk.sync.policy import DownPolicy
from b2sdk.sync.policy import UpAndDeletePolicy
from b2sdk.sync.policy import UpAndKeepDaysPolicy
from b2sdk.sync.policy import UpPolicy
from b2sdk.sync.policy import make_b2_keep_days_actions
from b2sdk.sync.policy_manager import SyncPolicyManager
from b2sdk.sync.report import SyncFileReporter
from b2sdk.sync.report import SyncReport
from b2sdk.sync.scan_policies import DEFAULT_SCAN_MANAGER
from b2sdk.sync.scan_policies import RegexSet
from b2sdk.sync.scan_policies import ScanPoliciesManager
from b2sdk.sync.sync import make_folder_sync_actions
from b2sdk.sync.sync import zip_folders

assert AbstractAction
assert AbstractFileSyncPolicy
assert AbstractFolder
assert B2DeleteAction
assert B2DownloadAction
assert B2Folder
assert B2HideAction
assert B2UploadAction
assert DEFAULT_SCAN_MANAGER
assert DownAndDeletePolicy
assert DownAndKeepDaysPolicy
assert DownPolicy
assert EnvironmentEncodingError
assert File
assert FileVersion
assert LocalDeleteAction
assert LocalFolder
assert RegexSet
assert ScanPoliciesManager
assert SyncFileReporter
assert SyncPolicyManager
assert SyncReport
assert UpAndDeletePolicy
assert UpAndKeepDaysPolicy
assert UpPolicy
assert make_b2_keep_days_actions
assert make_folder_sync_actions
assert parse_sync_folder
assert zip_folders

# other

from b2sdk.b2http import B2Http
from b2sdk.b2http import ClockSkewHook
from b2sdk.b2http import HttpCallback
from b2sdk.b2http import ResponseContextManager
from b2sdk.b2http import _translate_and_retry as translate_and_retry  # for some reason importing a _private thing didn't work in tests
from b2sdk.b2http import _translate_errors as translate_errors
from b2sdk.bounded_queue_executor import BoundedQueueExecutor
from b2sdk.cache import DummyCache
from b2sdk.session import B2Session

assert B2Http
assert B2Session
assert BoundedQueueExecutor
assert ClockSkewHook
assert DummyCache
assert HttpCallback
assert ResponseContextManager
assert translate_and_retry
assert translate_errors

######################################################################
#
# File: b2/sync/file.py
#
# Copyright 2019 Backblaze Inc. All Rights Reserved.
#
# License https://www.backblaze.com/using_b2_code.html
#
######################################################################


class File(object):
    """
    Holds information about one file in a folder.

    The name is relative to the folder in all cases.

    Files that have multiple versions (which only happens
    in B2, not in local folders) include information about
    all of the versions, most recent first.
    """

    def __init__(self, name, versions):
        self.name = name
        self.versions = versions

    def latest_version(self):
        return self.versions[0]

    def __repr__(self):
        return 'File(%s, [%s])' % (self.name, ', '.join(repr(v) for v in self.versions))


class FileVersion(object):
    """
    Holds information about one version of a file:
    """

    def __init__(self, id_, file_name, mod_time, action, size):
        """
        :param id_: the B2 file id, or the local full path name
        :param mod_time: modification time, in milliseconds, to avoid rounding issues 
        with millisecond times from B2
        :param action: "hide" or "upload" (never "start")
        """
        self.id_ = id_
        self.name = file_name
        self.mod_time = mod_time
        self.action = action
        self.size = size

    def __repr__(self):
        return 'FileVersion(%s, %s, %s, %s)' % (
            repr(self.id_), repr(self.name), repr(self.mod_time), repr(self.action)
        )

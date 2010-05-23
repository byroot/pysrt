# -*- coding: utf-8 -*-
import os
import sys
from UserList import UserList
from itertools import chain
from copy import copy
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from pysrt.srtexc import InvalidItem
from pysrt.srtitem import SubRipItem


class SubRipFile(UserList, object):
    """
    SubRip file descriptor.

    Provide a pure Python mapping on all metadata.

    SubRipFile(items, eol, path, encoding)

    items -> list of SubRipItem. Default to [].
    eol -> str: end of line character. Default to linesep used in opened file
        if any else to os.linesep.
    path -> str: path where file will be saved. To open an existant file see
        SubRipFile.open.
    encoding -> str: encoding used at file save. Default to utf-8.
    """
    ERROR_PASS = 0
    ERROR_LOG = 1
    ERROR_RAISE = 2

    def __init__(self, items=None, eol=None, path=None, encoding='utf-8'):
        UserList.__init__(self, items or [])
        self._eol = eol
        self.path = path
        self.encoding = encoding

    def _get_eol(self):
        return self._eol or os.linesep

    def _set_eol(self, eol):
        self._eol = self._eol or eol

    eol = property(_get_eol, _set_eol)

    @classmethod
    def _handle_error(cls, error, error_handling, path, index):
        path = os.path.abspath(path)
        if error_handling == cls.ERROR_RAISE:
            error.args = (path, index) + error.args
            raise error
        if error_handling == cls.ERROR_LOG:
            sys.stderr.write('PySRT-InvalidItem(%s:%s): \n' % (path, index))
            sys.stderr.write(error.args[0].encode('ascii', 'ignore'))
            sys.stderr.write('\n')

    @classmethod
    def open(cls, path='', encoding='utf-8', error_handling=ERROR_PASS,
             file_descriptor=None):
        """
        open([path, [encoding]])

        Encoding is set to utf-8 as default.
        """
        new_file = cls(path=path, encoding=encoding)

        if file_descriptor is None:
            source_file = open(path, 'rU')
        else:
            source_file = file_descriptor

        string_buffer = StringIO()
        for index, line in enumerate(chain(source_file, '\n')):
            if line.strip():
                string_buffer.write(line)
            else:
                string_buffer.seek(0)
                source = unicode(string_buffer.read(), new_file.encoding)
                try:
                    try:
                        new_item = SubRipItem.from_string(source)
                        new_file.append(new_item)
                    except InvalidItem, error:
                        cls._handle_error(error, error_handling, path, index)
                finally:
                    string_buffer.truncate(0)

        eol = cls._extract_newline(source_file)
        if eol is not None:
            new_file.eol = eol
        source_file.close()
        return new_file

    @staticmethod
    def _extract_newline(file_descriptor):
        if hasattr(file_descriptor, 'newlines') and file_descriptor.newlines:
            if isinstance(file_descriptor.newlines, basestring):
                return file_descriptor.newlines
            else:
                return file_descriptor.newlines[0]

    @classmethod
    def from_string(cls, source):
        return cls.open(file_descriptor=StringIO(source))

    def slice(self, starts_before=None, starts_after=None, ends_before=None,
              ends_after=None):
        clone = copy(self)

        if starts_before:
            clone.data = (i for i in clone.data if i.start < starts_before)
        if starts_after:
            clone.data = (i for i in clone.data if i.start > starts_after)
        if ends_before:
            clone.data = (i for i in clone.data if i.end < ends_before)
        if ends_after:
            clone.data = (i for i in clone.data if i.end > ends_after)

        clone.data = list(clone.data)
        return clone

    def shift(self, *args, **kwargs):
        """
        shift(hours, minutes, seconds, milliseconds)

        Add given values to start and end attributes of each items of file
        with given values.
        All arguments are optional and have a default value of 0.
        """
        for item in self:
            item.shift(*args, **kwargs)

    def clean_indexes(self):
        self.sort()
        for index, item in enumerate(self):
            item.index = index + 1

    def save(self, path=None, encoding=None, eol=None):
        """
        save([path][, encoding][, eol])

        Use init path if no other provided.
        Use init encoding if no other provided.
        Use init eol if no other provided.
        """
        path = path or self.path
        encoding = encoding or self.encoding
        output_eol = eol or self.eol

        save_file = open(path, 'w+')
        for item in self:
            string_repr = unicode(item)
            if output_eol != '\n':
                string_repr = string_repr.replace('\n', output_eol)
            save_file.write(string_repr.encode(encoding))
        save_file.close()

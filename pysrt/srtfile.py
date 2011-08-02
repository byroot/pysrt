# -*- coding: utf-8 -*-
import os
import sys
import codecs
from UserList import UserList
from itertools import chain
from copy import copy

from pysrt.srtexc import InvalidItem
from pysrt.srtitem import SubRipItem

BOMS = ((codecs.BOM_UTF32_LE, 'utf_32_le'),
        (codecs.BOM_UTF32_BE, 'utf_32_be'),
        (codecs.BOM_UTF16_LE, 'utf_16_le'),
        (codecs.BOM_UTF16_BE, 'utf_16_be'),
        (codecs.BOM_UTF8, 'utf_8'))
CODECS_BOMS = dict((codec, unicode(bom, codec)) for bom, codec in BOMS)
BIGGER_BOM = max(len(bom) for bom, encoding in BOMS)


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

    DEFAULT_ENCODING = 'utf_8'

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

    def slice(self, starts_before=None, starts_after=None, ends_before=None,
              ends_after=None):
        """
        slice([starts_before][, starts_after][, ends_before][, ends_after]) \
-> SubRipFile clone

        All arguments are optional, and should be coercible to SubRipTime
        object.

        It reduce the set of subtitles to those that match match given time
        constraints.

        The returned set is a clone, but still contains references to original
        subtitles. So if you shift this returned set, subs contained in the
        original SubRipFile instance will be altered too.

        Example:
            >>> subs.slice(ends_after={'seconds': 20}).shift(seconds=2)
        """
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
        """shift(hours, minutes, seconds, milliseconds, ratio)

        Shift `start` and `end` attributes of each items of file either by
        applying a ratio or by adding an offset.

        `ratio` should be either an int or a float.
        Example to convert subtitles from 23.9 fps to 25 fps:
        >>> subs.shift(ratio=25/23.9)

        All "time" arguments are optional and have a default value of 0.
        Example to delay all subs from 2 seconds and half
        >>> subs.shift(seconds=2, milliseconds=500)
        """
        for item in self:
            item.shift(*args, **kwargs)

    def clean_indexes(self):
        self.sort()
        for index, item in enumerate(self):
            item.index = index + 1

    @classmethod
    def open(cls, path='', encoding=None, error_handling=ERROR_PASS, eol=None):
        """
        open([path, [encoding]])

        If you do not provide any encoding, it can be detected if the file
        contain a bit order mark, unless it is set to utf-8 as default.
        """
        new_file = cls(path=path, encoding=encoding)
        source_file = cls._open_unicode_file(path, claimed_encoding=encoding)
        new_file.read(source_file, error_handling=error_handling)
        eol = eol or cls._extract_newline(source_file)
        if eol is not None:
            new_file.eol = eol
        source_file.close()
        return new_file

    @classmethod
    def from_string(cls, source, **kwargs):
        """
        from_string(source, **kwargs) -> SubRipFile

        `source` -> a unicode instance or at least a str instance encoded with
        `sys.getdefaultencoding()`
        """
        error_handling = kwargs.pop('error_handling', None)
        new_file = cls(**kwargs)
        new_file.read(source.splitlines(True), error_handling=error_handling)
        return new_file

    def read(self, source_file, error_handling=ERROR_PASS):
        """
        read(source_file, [error_handling])

        This method parse subtitles contained in `source_file` and append them
        to the current instance.

        `source_file` -> Any iterable that yield unicode strings, like a file
            opened with `codecs.open()` or an array of unicode.
        """
        self.extend(self.stream(source_file, error_handling=error_handling))
        return self

    @classmethod
    def stream(cls, source_file, error_handling=ERROR_PASS):
        """
        stream(source_file, [error_handling])

        This method yield SubRipItem instances a soon as they have been parsed
        without storing them. It is a kind of SAX parser for .srt files.

        `source_file` -> Any iterable that yield unicode strings, like a file
            opened with `codecs.open()` or an array of unicode.

        Example:
            >>> from pysrt import SubRipFile
            >>> import codecs
            >>> file = codecs.open('movie.srt', encoding='utf-8')
            >>> for sub in SubRipFile.stream(file):
            ...     sub.text += "\nHello !"
            ...     print unicode(sub)
        """
        string_buffer = []
        for index, line in enumerate(chain(source_file, u'\n')):
            if line.strip():
                string_buffer.append(line)
            else:
                source = u''.join(string_buffer)
                string_buffer = []
                if source.strip():
                    try:
                        yield SubRipItem.from_string(source)
                    except InvalidItem, error:
                        cls._handle_error(error, error_handling, index)

    def save(self, path=None, encoding=None, eol=None):
        """
        save([path][, encoding][, eol])

        Use init path if no other provided.
        Use init encoding if no other provided.
        Use init eol if no other provided.
        """
        path = path or self.path
        encoding = encoding or self.encoding

        save_file = codecs.open(path, 'w+', encoding=encoding)
        self.write_into(save_file, eol=eol)
        save_file.close()

    def write_into(self, output_file, eol=None):
        """
        write_into(output_file [, eol])

        Serialize current state into `output_file`.

        `output_file` -> Any instance that respond to `write()`, typically a
        file object
        """
        output_eol = eol or self.eol

        for item in self:
            string_repr = unicode(item)
            if output_eol != '\n':
                string_repr = string_repr.replace('\n', output_eol)
            output_file.write(string_repr)

    @staticmethod
    def _extract_newline(file_descriptor):
        if hasattr(file_descriptor, 'newlines') and file_descriptor.newlines:
            if isinstance(file_descriptor.newlines, basestring):
                return file_descriptor.newlines
            else:
                return file_descriptor.newlines[0]

    @classmethod
    def _detect_encoding(cls, path):
        file_descriptor = open(path)
        first_chars = file_descriptor.read(BIGGER_BOM)
        file_descriptor.close()

        for bom, encoding in BOMS:
            if first_chars.startswith(bom):
                return encoding

        # TODO: maybe a chardet integration
        return cls.DEFAULT_ENCODING

    @classmethod
    def _open_unicode_file(cls, path, claimed_encoding=None):
        encoding = claimed_encoding or cls._detect_encoding(path)
        source_file = codecs.open(path, 'rU', encoding=encoding)

        # get rid of BOM if any
        possible_bom = CODECS_BOMS.get(encoding, None)
        if possible_bom:
            file_bom = source_file.read(len(possible_bom))
            if not file_bom == possible_bom:
                source_file.seek(0) # if not rewind
        return source_file

    @classmethod
    def _handle_error(cls, error, error_handling, index):
        if error_handling == cls.ERROR_RAISE:
            error.args = (index, ) + error.args
            raise error
        if error_handling == cls.ERROR_LOG:
            sys.stderr.write('PySRT-InvalidItem(line %s): \n' % index)
            sys.stderr.write(error.args[0].encode('ascii', 'replace'))
            sys.stderr.write('\n')

# -*- coding: utf-8 -*-
from os.path import exists, isfile
from UserList import UserList
from itertools import chain
from copy import copy
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from srtitem import SubRipItem

class SubRipFile(UserList, object):
    """
    SubRip file descriptor.

    Provide a pure Python mapping on all metadata.
    """

    def __init__(self, items=None, eol=None):
        UserList.__init__(self, items or [])
        self._eol = eol

    def _get_eol(self):
        return self._eol or DEFAULT_EOL

    def _set_eol(self, eol):
        self._eol = self._eol or eol

    eol = property(_get_eol, _set_eol)

    @classmethod
    def open(cls, path='', encoding='utf-8'):
        """
        open([path, [encoding]])

        Encoding is set to utf-8 as default.
        """
        new_file = cls()
        new_file.encoding = encoding
        new_file.path = path

        if isinstance(path, basestring):
            source_file = open(path, 'rU')
        else:
            source_file = path

        string_buffer = StringIO()
        for line in chain(source_file, '\n'):
            if line.strip():
                string_buffer.write(line)
            else:
                string_buffer.seek(0)
                source = unicode(string_buffer.read(), new_file.encoding)
                if source:
                    new_item = SubRipItem.from_string(source)
                    new_file.append(new_item)
                    string_buffer.truncate(0)

        if hasattr(new_file, 'newlines') and new_file.newlines:
            new_file.eol = tuple(source_file.newlines)[0]

        source_file.close()
        return new_file

    @classmethod
    def from_string(cls, source):
        return cls.open(StringIO(source))

    def slice(self, starts_before=None, starts_after=None, ends_before=None, ends_after=None):
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
        shift(hours, minutes, seconds, micro_seconds)

        Add given values to start and end attributes of each items of file
        with given values.
        All arguments are optional and have a default value of 0.
        """
        for item in self:
            item.shift(*args, **kwargs)

    def clean_ids(self):
        self.sort()
        for index, item in enumerate(self):
            self[index].id = index + 1

    def save(self, path=None, encoding=None, eol=None):
        """
        save([path][, encoding][, eol])

        Use init path if no other provided.
        Use init encoding if no other provided.
        Use init eol if no other provided.
        """
        path = path or self.path
        encoding = encoding or self.encoding
        eol = eol or self.eol

        save_file = open(path, 'w+')
        for item in self:
            save_file.write(unicode(item).replace('\n', eol).encode(encoding))
        save_file.close()

# -*- coding: utf-8 -*-
"""
SubRip's subtitle parser
"""
import os
import re

from pysrt.srtexc import InvalidItem
from pysrt.srttime import SubRipTime


class SubRipItem(object):
    """
    SubRipItem(sub_id, start, end, sub_title)

    sub_id -> int: index of item in file. 0 by default.
    start, end -> SubRipTime or coercable.
    sub_title -> unicode: text content for item.
    """
    RE_ITEM = re.compile(r'''(?P<index>\d+)
(?P<start>\d{2}:\d{2}:\d{2},\d{3}) --> (?P<end>\d{2}:\d{2}:\d{2},\d{3})
(?P<text>.*)''', re.DOTALL)
    ITEM_PATTERN = u'%s\n%s --> %s\n%s\n'.replace('\n', os.linesep)

    def __init__(self, index=0, start=None, end=None, text=''):
        self.index = int(index)
        self.start = start or SubRipTime()
        self.end = end or SubRipTime()
        self.text = unicode(text)

    def __unicode__(self):
        return self.ITEM_PATTERN % (self.index, self.start, self.end,
                                    self.text)

    def __cmp__(self, other):
        return cmp(self.start, other.start) \
            or cmp(self.end, other.end)

    def shift(self, *args, **kwargs):
        """
        shift(hours, minutes, seconds, milliseconds)

        Add given values to start and end attributes.
        All arguments are optional and have a default value of 0.
        """
        self.start.shift(*args, **kwargs)
        self.end.shift(*args, **kwargs)

    @classmethod
    def from_string(cls, source):
        match = cls.RE_ITEM.match(source)
        if not match:
            raise InvalidItem(source)

        data = dict(match.groupdict())
        for group in ('start', 'end'):
            data[group] = SubRipTime.from_string(data[group])
        return cls(**data)

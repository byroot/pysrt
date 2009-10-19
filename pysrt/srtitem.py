# -*- coding: utf-8 -*-
import os
import re

from srtexc import InvalidItem
from srttime import SubRipTime


class SubRipItem(object):

    RE_ITEM = re.compile(r'''(?P<sub_id>\d+)
(?P<start>\d{2}:\d{2}:\d{2},\d{3}) --> (?P<end>\d{2}:\d{2}:\d{2},\d{3})
(?P<sub_title>.*)''', re.DOTALL)
    ITEM_PATTERN = u'%s\n%s --> %s\n%s\n'.replace('\n', os.linesep)

    def __init__(self, sub_id=0, start=None, end=None, sub_title=''):
        self.id = int(sub_id)
        self.start = start or SubRipTime()
        self.end = end or SubRipTime()
        self.sub_title = unicode(sub_title)

    def __unicode__(self):
        return self.ITEM_PATTERN % (self.id,
            self.start, self.end, self.sub_title)

    def __cmp__(self, other):
        return cmp(self.start, other.start) \
            or cmp(self.end, other.end)

    def shift(self, *args, **kwargs):
        """
        shift(hours, minutes, seconds, micro_seconds)

        Add given values to start and end attributes.
        All arguments are optional and have a default value of 0.
        """
        self.start.shift(*args, **kwargs)
        self.end.shift(*args, **kwargs)

    @classmethod
    def from_string(cls, source):
        match = cls.RE_ITEM.match(source)
        if not match:
            raise InvalidItem

        data = dict(match.groupdict())
        for group in ('start', 'end'):
            data[group] = SubRipTime.from_string(data[group])
        return cls(**data)

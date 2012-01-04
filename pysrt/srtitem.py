# -*- coding: utf-8 -*-
"""
SubRip's subtitle parser
"""
from pysrt.srtexc import InvalidItem
from pysrt.srttime import SubRipTime


class SubRipItem(object):
    """
    SubRipItem(index, start, end, text, position)

    index -> int: index of item in file. 0 by default.
    start, end -> SubRipTime or coercible.
    text -> unicode: text content for item.
    position -> unicode: raw srt/vtt "display coordinates" string
    """
    ITEM_PATTERN = u'%s\n%s --> %s%s\n%s\n'

    def __init__(self, index=0, start=None, end=None, text=u'', position=u''):
        self.index = int(index)
        self.start = SubRipTime.coerce(start or 0)
        self.end = SubRipTime.coerce(end or 0)
        self.position = unicode(position)
        self.text = unicode(text)

    def __unicode__(self):
        position = ' %s' % self.position if self.position.strip() else ''
        return self.ITEM_PATTERN % (self.index, self.start, self.end,
                                    position, self.text)

    def __cmp__(self, other):
        return cmp(self.start, other.start) \
            or cmp(self.end, other.end)

    def shift(self, *args, **kwargs):
        """
        shift(hours, minutes, seconds, milliseconds, ratio)

        Add given values to start and end attributes.
        All arguments are optional and have a default value of 0.
        """
        self.start.shift(*args, **kwargs)
        self.end.shift(*args, **kwargs)

    @classmethod
    def from_string(cls, source):
        return cls.from_lines(source.splitlines(True))

    @classmethod
    def from_lines(cls, lines):
        if len(lines) < 3:
            raise InvalidItem()
        lines = [l.replace('\r', '') for l in lines]
        index = lines[0]
        start, end, position = cls.split_timestamps(lines[1])
        body = u''.join(lines[2:])
        return cls(index, start, end, body, position)

    @staticmethod
    def split_timestamps(line):
        start, end_and_position = line.split('-->')
        end_and_position = end_and_position.lstrip().split(' ', 1)
        end = end_and_position[0]
        position = end_and_position[1] if len(end_and_position) > 1 else ''
        return (s.strip() for s in (start, end, position))

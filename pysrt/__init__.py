# -*- coding: utf-8 -*-
'''
>>> s = SubRipFile.from_string("""1
... 00:00:02,207 --> 00:00:03,221
... ÉCHEC !
...
... 2
... 00:00:30,371 --> 00:00:33,981
... Le Retour de l'Enfant Prodigue
...
... 3
... 00:00:35,619 --> 00:00:37,277
... Ce qui veut dire...
...
... 4
... 00:00:37,433 --> 00:00:39,761
... un bénéfice, cette année, de...
...
... 5
... 00:00:39,933 --> 00:00:43,121
... - 1 800 milliards de milliards.
... - Splendide !
...
... 7
... 00:00:43,410 --> 00:00:45,136
... Sans compter les revenus subsidiaires
... """)
>>> len(s)
6
>>> s.clean_ids()
>>> s[5].id
6
>>> s[-1].end.seconds
45
>>> part = SubRipFile(i for i in s if i.end > (0, 0, 40))
>>> len(part)
2
>>> part = SubRipFile(i for i in s if i.end > {'seconds': 40})
>>> len(part)
2
>>> part.shift(seconds=-5)
>>> part[1].start.minutes += 5
>>> item = s[-1]
>>> item.end.seconds
40
>>> tuple(item.start), tuple(SubRipTime(*tuple(item.start)))
((0, 5, 38, 410), (0, 5, 38, 410))
>>> tuple(item.start) == SubRipTime(*tuple(item.start))
True
>>> item.start <= (0, 5, 39)
True
>>> item.start >= (0, 5, 37)
True
>>> item.start == (0, 5, 38, 410)
True

>>> t= SubRipTime(micro_seconds=1)
>>> t.seconds, t.ordinal
(0, 1)
>>> t.seconds += 1
>>> t.seconds, t.ordinal
(1, 1001)
>>> tuple(t + {'seconds': 1})
(0, 0, 2, 1)
>>> tuple(t - {'seconds': 1})
(0, 0, 0, 1)

'''
__all__ = ['SubRipFile', 'SubRipItem', 'SubRipTime']
import re
from itertools import chain
from os.path import exists, isfile
from UserList import UserList
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

DEFAULT_EOL = '\n' # TODO: no standard constant / function for that ?

class InvalidItem(Exception):
    pass


class TimeItemDescriptor(object):

    def __init__(self, ratio, super_ratio=None):
        self.ratio = int(ratio)
        self.super_ratio = int(super_ratio) if super_ratio else None

    def __get__(self, instance, klass):
        if instance is None:
            raise AttributeError
        if self.super_ratio:
            return (instance.ordinal % self.super_ratio) / self.ratio
        return instance.ordinal / self.ratio

    def __set__(self, instance, value):
        base_ord = instance.ordinal
        if self.super_ratio:
            base_ord %= self.super_ratio
        current_part = base_ord - instance.ordinal % self.ratio
        instance.ordinal += value * self.ratio - current_part


class SubRipTime(object):
    STRING_FORMAT = '%02d:%02d:%02d,%03d'
    RE_TIME = re.compile(r'''(?P<hours>\d{2}):
                             (?P<minutes>\d{2}):
                             (?P<seconds>\d{2}),
                             (?P<micro_seconds>\d{3})''',
                             re.VERBOSE)
    SECONDS_RATIO = 1000
    MINUTES_RATIO = SECONDS_RATIO * 60
    HOURS_RATIO = MINUTES_RATIO * 60

    hours = TimeItemDescriptor(HOURS_RATIO)
    minutes = TimeItemDescriptor(MINUTES_RATIO, HOURS_RATIO)
    seconds = TimeItemDescriptor(SECONDS_RATIO, MINUTES_RATIO)
    micro_seconds = TimeItemDescriptor(1, SECONDS_RATIO)

    def __init__(self, hours=0, minutes=0, seconds=0, micro_seconds=0):
        """
        SubRipTime(hours, minutes, seconds, micro_seconds)

        All arguments are optional and have a default value of 0.
        """
        self.ordinal = hours * self.HOURS_RATIO \
                     + minutes * self.MINUTES_RATIO \
                     + seconds * self.SECONDS_RATIO \
                     + micro_seconds

    def __unicode__(self):
        return unicode(self.STRING_FORMAT) % (self.hours,
            self.minutes, self.seconds, self.micro_seconds)

    def __cmp__(self, other):
        return cmp(self.ordinal, self._coerce(other).ordinal)

    def __add__(self, other):
        return self.from_ordinal(self.ordinal + self._coerce(other).ordinal)

    def __iadd__(self, other):
        self.ordinal += self._coerce(other).ordinal

    def __sub__(self, other):
        return self.from_ordinal(self.ordinal - self._coerce(other).ordinal)

    def __isub__(self, other):
        self.ordinal -= self._coerce(other).ordinal

    @classmethod
    def _coerce(cls, other):
        if isinstance(other, SubRipTime):
            return other
        try:
            return cls(**other)
        except TypeError:
            return cls(*other)

    def __iter__(self):
        yield self.hours
        yield self.minutes
        yield self.seconds
        yield self.micro_seconds

    def shift(self, *args, **kwargs):
        """
        shift(hours, minutes, seconds, micro_seconds)

        All arguments are optional and have a default value of 0.
        """
        self += self.__class__(*args, **kwargs)

    @classmethod
    def from_ordinal(cls, ordinal):
        new_time = cls()
        new_time.ordinal = int(ordinal)
        return new_time

    @classmethod
    def from_string(cls, source):
        match = re.match(cls.RE_TIME, source)
        if not match:
            raise InvalidItem
        items = dict((k, int(v)) for k, v in match.groupdict().items())
        return cls(**items)


class SubRipItem(object):

    RE_ITEM = r'''(?P<sub_id>\d+)
(?P<start>\d{2}:\d{2}:\d{2},\d{3}) --> (?P<end>\d{2}:\d{2}:\d{2},\d{3})
(?P<sub_title>.*)'''
    ITEM_PATTERN = u'%s\n%s --> %s\n%s\n'

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
        match = re.match(cls.RE_ITEM, source, re.DOTALL)
        if not match:
            raise InvalidItem
        data = dict(match.groupdict())
        data['start'] = SubRipTime.from_string(data['start'])
        data['end'] = SubRipTime.from_string(data['end'])
        return cls(**data)


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

if __name__ == "__main__":
    import doctest
    doctest.testmod()

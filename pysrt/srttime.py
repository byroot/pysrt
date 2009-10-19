# -*- coding: utf-8 -*-
import re


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

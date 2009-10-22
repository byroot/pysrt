#!/usr/bin/env python

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pysrt import SubRipTime


class TestSimpleTime:
    def setUp(self):
        self.time = SubRipTime()
        
    def test_default_value(self):
        assert self.time.ordinal == 0
        
    def test_micro_seconds(self):
        self.time.milliseconds = 1
        assert self.time.milliseconds == 1
        self.time.hours += 42
        assert self.time.milliseconds == 1
        self.time.milliseconds += 1000
        assert self.time.seconds == 1

    def test_seconds(self):
        self.time.seconds = 1
        assert self.time.seconds == 1
        self.time.hours += 42
        assert self.time.seconds == 1
        self.time.seconds += 60
        assert self.time.minutes == 1
    
    def test_minutes(self):
        self.time.minutes = 1
        assert self.time.minutes == 1
        self.time.hours += 42
        assert self.time.minutes == 1
        self.time.minutes += 60
        assert self.time.hours == 43
    
    def test_hours(self):
        self.time.hours = 1
        assert self.time.hours == 1
        self.time.minutes += 42
        assert self.time.hours == 1


class TestTimeParsing:
    KNOWN_VALUES = (
        ('00:00:00,000', (0, 0, 0, 0)),
        ('00:00:00,001', (0, 0, 0, 1)),
        ('00:00:02,000', (0, 0, 2, 0)),
        ('00:03:00,000', (0, 3, 0, 0)),
        ('04:00:00,000', (4, 0, 0, 0)),
        ('12:34:56,789', (12, 34, 56, 789)),
    )
    
    def test_parsing(self):
        for time_string, time_items in self.KNOWN_VALUES:
            assert SubRipTime.from_string(time_string) == SubRipTime(*time_items)

    def test_serialization(self):
        for time_string, time_items in self.KNOWN_VALUES:
            assert time_string == str(SubRipTime(*time_items))


class TestCoercing:
    def test_from_tuple(self):
        assert (0, 0, 0, 0) == SubRipTime()
        assert (0, 0, 0, 1) == SubRipTime(milliseconds=1)
        assert (0, 0, 2, 0) == SubRipTime(seconds=2)
        assert (0, 3, 0, 0) == SubRipTime(minutes=3)
        assert (4, 0, 0, 0) == SubRipTime(hours=4)
        assert (1, 2, 3, 4) == SubRipTime(1, 2, 3, 4)

    def test_from_dict(self):
        assert dict() == SubRipTime()
        assert dict(milliseconds=1) == SubRipTime(milliseconds=1)
        assert dict(seconds=2) == SubRipTime(seconds=2)
        assert dict(minutes=3) == SubRipTime(minutes=3)
        assert dict(hours=4) == SubRipTime(hours=4)
        assert dict(hours=1, minutes=2, seconds=3, milliseconds=4) == SubRipTime(1, 2, 3, 4)
        
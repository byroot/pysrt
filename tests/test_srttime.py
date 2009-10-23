#!/usr/bin/env python

import os
import sys
from datetime import time
import unittest

file_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, os.path.abspath(file_path))

from pysrt import SubRipTime


class TestSimpleTime(unittest.TestCase):

    def setUp(self):
        self.time = SubRipTime()

    def test_default_value(self):
        self.assertEquals(self.time.ordinal, 0)

    def test_micro_seconds(self):
        self.time.milliseconds = 1
        self.assertEquals(self.time.milliseconds, 1)
        self.time.hours += 42
        self.assertEquals(self.time.milliseconds, 1)
        self.time.milliseconds += 1000
        self.assertEquals(self.time.seconds, 1)

    def test_seconds(self):
        self.time.seconds = 1
        self.assertEquals(self.time.seconds, 1)
        self.time.hours += 42
        self.assertEquals(self.time.seconds, 1)
        self.time.seconds += 60
        self.assertEquals(self.time.minutes, 1)

    def test_minutes(self):
        self.time.minutes = 1
        self.assertEquals(self.time.minutes, 1)
        self.time.hours += 42
        self.assertEquals(self.time.minutes, 1)
        self.time.minutes += 60
        self.assertEquals(self.time.hours, 43)

    def test_hours(self):
        self.time.hours = 1
        self.assertEquals(self.time.hours, 1)
        self.time.minutes += 42
        self.assertEquals(self.time.hours, 1)


class TestTimeParsing(unittest.TestCase):
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
            self.assertEquals(time_string, SubRipTime(*time_items))

    def test_serialization(self):
        for time_string, time_items in self.KNOWN_VALUES:
            self.assertEquals(time_string, str(SubRipTime(*time_items)))


class TestCoercing(unittest.TestCase):

    def test_from_tuple(self):
        self.assertEquals((0, 0, 0, 0), SubRipTime())
        self.assertEquals((0, 0, 0, 1), SubRipTime(milliseconds=1))
        self.assertEquals((0, 0, 2, 0), SubRipTime(seconds=2))
        self.assertEquals((0, 3, 0, 0), SubRipTime(minutes=3))
        self.assertEquals((4, 0, 0, 0), SubRipTime(hours=4))
        self.assertEquals((1, 2, 3, 4), SubRipTime(1, 2, 3, 4))

    def test_from_dict(self):
        self.assertEquals(dict(), SubRipTime())
        self.assertEquals(dict(milliseconds=1), SubRipTime(milliseconds=1))
        self.assertEquals(dict(seconds=2), SubRipTime(seconds=2))
        self.assertEquals(dict(minutes=3), SubRipTime(minutes=3))
        self.assertEquals(dict(hours=4), SubRipTime(hours=4))
        self.assertEquals(dict(hours=1, minutes=2, seconds=3, milliseconds=4),
            SubRipTime(1, 2, 3, 4))

    def test_from_time(self):
        assert SubRipTime(1, 2, 3, 4) == time(1, 2, 3, 4000)
        assert SubRipTime(1, 2, 3, 5) >= time(1, 2, 3, 4000)
        assert SubRipTime(1, 2, 3, 3) <= time(1, 2, 3, 4000)
        assert SubRipTime(1, 2, 3, 0) != time(1, 2, 3, 4000)

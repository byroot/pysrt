#!/usr/bin/env python

import os
import sys
from datetime import time
import unittest

file_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, os.path.abspath(file_path))

from pysrt import SubRipTime, InvalidTimeString


class TestSimpleTime(unittest.TestCase):

    def setUp(self):
        self.time = SubRipTime()

    def test_default_value(self):
        self.assertEqual(self.time.ordinal, 0)

    def test_micro_seconds(self):
        self.time.milliseconds = 1
        self.assertEqual(self.time.milliseconds, 1)
        self.time.hours += 42
        self.assertEqual(self.time.milliseconds, 1)
        self.time.milliseconds += 1000
        self.assertEqual(self.time.seconds, 1)

    def test_seconds(self):
        self.time.seconds = 1
        self.assertEqual(self.time.seconds, 1)
        self.time.hours += 42
        self.assertEqual(self.time.seconds, 1)
        self.time.seconds += 60
        self.assertEqual(self.time.minutes, 1)

    def test_minutes(self):
        self.time.minutes = 1
        self.assertEqual(self.time.minutes, 1)
        self.time.hours += 42
        self.assertEqual(self.time.minutes, 1)
        self.time.minutes += 60
        self.assertEqual(self.time.hours, 43)

    def test_hours(self):
        self.time.hours = 1
        self.assertEqual(self.time.hours, 1)
        self.time.minutes += 42
        self.assertEqual(self.time.hours, 1)

    def test_shifting(self):
        self.time.shift(1, 1, 1, 1)
        self.assertEqual(self.time, (1, 1, 1, 1))

    def test_descriptor_from_class(self):
        self.assertRaises(AttributeError, lambda: SubRipTime.hours)


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
            self.assertEqual(time_string, SubRipTime(*time_items))

    def test_serialization(self):
        for time_string, time_items in self.KNOWN_VALUES:
            self.assertEqual(time_string, str(SubRipTime(*time_items)))

    def test_negative_serialization(self):
        self.assertEqual('00:00:00,000', str(SubRipTime(-1, 2, 3, 4)))

    def test_invalid_time_string(self):
        self.assertRaises(InvalidTimeString, SubRipTime.from_string, 'hello')


class TestCoercing(unittest.TestCase):

    def test_from_tuple(self):
        self.assertEqual((0, 0, 0, 0), SubRipTime())
        self.assertEqual((0, 0, 0, 1), SubRipTime(milliseconds=1))
        self.assertEqual((0, 0, 2, 0), SubRipTime(seconds=2))
        self.assertEqual((0, 3, 0, 0), SubRipTime(minutes=3))
        self.assertEqual((4, 0, 0, 0), SubRipTime(hours=4))
        self.assertEqual((1, 2, 3, 4), SubRipTime(1, 2, 3, 4))

    def test_from_dict(self):
        self.assertEqual(dict(), SubRipTime())
        self.assertEqual(dict(milliseconds=1), SubRipTime(milliseconds=1))
        self.assertEqual(dict(seconds=2), SubRipTime(seconds=2))
        self.assertEqual(dict(minutes=3), SubRipTime(minutes=3))
        self.assertEqual(dict(hours=4), SubRipTime(hours=4))
        self.assertEqual(dict(hours=1, minutes=2, seconds=3, milliseconds=4),
            SubRipTime(1, 2, 3, 4))

    def test_from_time(self):
        time_obj = time(1, 2, 3, 4000)
        self.assertEqual(SubRipTime(1, 2, 3, 4), time_obj)
        self.assertTrue(SubRipTime(1, 2, 3, 5) >= time_obj)
        self.assertTrue(SubRipTime(1, 2, 3, 3) <= time_obj)
        self.assertTrue(SubRipTime(1, 2, 3, 0) != time_obj)
        self.assertEqual(SubRipTime(1, 2, 3, 4).to_time(), time_obj)
        self.assertTrue(SubRipTime(1, 2, 3, 5).to_time() >= time_obj)
        self.assertTrue(SubRipTime(1, 2, 3, 3).to_time() <= time_obj)
        self.assertTrue(SubRipTime(1, 2, 3, 0).to_time() != time_obj)

    def test_from_ordinal(self):
        self.assertEqual(SubRipTime.from_ordinal(3600000), {'hours': 1})
        self.assertEqual(SubRipTime(1), 3600000)


class TestOperators(unittest.TestCase):

    def setUp(self):
        self.time = SubRipTime(1, 2, 3, 4)

    def test_add(self):
        self.assertEqual(self.time + (1, 2, 3, 4), (2, 4, 6, 8))

    def test_iadd(self):
        self.time += (1, 2, 3, 4)
        self.assertEqual(self.time, (2, 4, 6, 8))

    def test_sub(self):
        self.assertEqual(self.time - (1, 2, 3, 4), 0)

    def test_isub(self):
        self.time -= (1, 2, 3, 4)
        self.assertEqual(self.time, 0)

    def test_mul(self):
        self.assertEqual(self.time * 2,  SubRipTime(2, 4, 6, 8))
        self.assertEqual(self.time * 0.5,  (0, 31, 1, 502))

    def test_imul(self):
        self.time *= 2
        self.assertEqual(self.time,  (2, 4, 6, 8))
        self.time *= 0.5
        self.assertEqual(self.time, (1, 2, 3, 4))

    def test_div(self):
        self.assertEqual(self.time / 0.5, SubRipTime(2, 4, 6, 8))
        self.assertEqual(self.time / 2, (0, 31, 1, 502))


    def test_idiv(self):
        self.time /= 0.5
        self.assertEqual(self.time, (2, 4, 6, 8))
        self.time /= 2
        self.assertEqual(self.time, (1, 2, 3, 4))

if __name__ == '__main__':
    unittest.main()

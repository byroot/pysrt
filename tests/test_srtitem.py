#!/usr/bin/env python

import os
import sys
from datetime import time
import unittest

file_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, os.path.abspath(file_path))

from pysrt import SubRipItem, SubRipTime, InvalidItem


class TestAttributes(unittest.TestCase):

    def setUp(self):
        self.item = SubRipItem()

    def test_has_id(self):
        self.assertTrue(hasattr(self.item, 'index'))
        self.assertTrue(isinstance(self.item.index, int))

    def test_has_content(self):
        self.assertTrue(hasattr(self.item, 'text'))
        self.assertTrue(isinstance(self.item.text, unicode))

    def test_has_start(self):
        self.assertTrue(hasattr(self.item, 'start'))
        self.assertTrue(isinstance(self.item.start, SubRipTime))

    def test_has_end(self):
        self.assertTrue(hasattr(self.item, 'end'))
        self.assertTrue(isinstance(self.item.end, SubRipTime))


class TestShifting(unittest.TestCase):

    def setUp(self):
        self.item = SubRipItem(1, text="Hello world !")
        self.item.shift(minutes=1)
        self.item.end.shift(seconds=20)

    def test_shift_up(self):
        self.item.shift(1, 2, 3, 4)
        self.assertEqual(self.item.start, (1, 3, 3, 4))
        self.assertEqual(self.item.end, (1, 3, 23, 4))

    def test_shift_down(self):
        self.item.shift(5)
        self.item.shift(-1, -2, -3, -4)
        self.assertEqual(self.item.start, (3, 58, 56, 996))
        self.assertEqual(self.item.end, (3, 59, 16, 996))


class TestOperators(unittest.TestCase):

    def setUp(self):
        self.item = SubRipItem(1, text="Hello world !")
        self.item.shift(minutes=1)
        self.item.end.shift(seconds=20)

    def test_cmp(self):
        self.assertEquals(self.item, self.item)


class TestSerialAndParsing(unittest.TestCase):

    def setUp(self):
        self.item = SubRipItem(1, text="Hello world !")
        self.item.shift(minutes=1)
        self.item.end.shift(seconds=20)
        self.string = u'1\n00:01:00,000 --> 00:01:20,000\nHello world !\n'
        self.bad_string = u'foobar'

    def test_serialization(self):
        self.assertEqual(unicode(self.item), self.string)

    def test_from_string(self):
        self.assertEquals(SubRipItem.from_string(self.string), self.item)
        self.assertRaises(InvalidItem, SubRipItem.from_string,
            self.bad_string)

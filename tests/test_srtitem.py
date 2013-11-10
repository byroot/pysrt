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
        self.assertTrue(isinstance(self.item.text, str))

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

    def test_shift_by_ratio(self):
        self.item.shift(ratio=2)
        self.assertEqual(self.item.start, {'minutes': 2})
        self.assertEqual(self.item.end, {'minutes': 2, 'seconds': 40})


class TestOperators(unittest.TestCase):

    def setUp(self):
        self.item = SubRipItem(1, text="Hello world !")
        self.item.shift(minutes=1)
        self.item.end.shift(seconds=20)

    def test_cmp(self):
        self.assertEqual(self.item, self.item)


class TestSerialAndParsing(unittest.TestCase):

    def setUp(self):
        self.item = SubRipItem(1, text="Hello world !")
        self.item.shift(minutes=1)
        self.item.end.shift(seconds=20)
        self.string = '1\n00:01:00,000 --> 00:01:20,000\nHello world !\n'
        self.bad_string = 'foobar'
        self.coordinates = ('1\n00:01:00,000 --> 00:01:20,000 X1:000 X2:000 '
                                'Y1:050 Y2:100\nHello world !\n')
        self.vtt = ('1\n00:01:00,000 --> 00:01:20,000 D:vertical A:start '
                                'L:12%\nHello world !\n')
        self.string_index = 'foo\n00:01:00,000 --> 00:01:20,000\nHello !\n'
        self.dots = '1\n00:01:00.000 --> 00:01:20.000\nHello world !\n'
        self.no_index = '00:01:00,000 --> 00:01:20,000\nHello world !\n'
        self.junk_after_timestamp = ('1\n00:01:00,000 --> 00:01:20,000?\n'
                                'Hello world !\n')

    def test_serialization(self):
        self.assertEqual(str(self.item), self.string)

    def test_from_string(self):
        self.assertEqual(SubRipItem.from_string(self.string), self.item)
        self.assertRaises(InvalidItem, SubRipItem.from_string,
            self.bad_string)

    def test_coordinates(self):
        item = SubRipItem.from_string(self.coordinates)
        self.assertEqual(item, self.item)
        self.assertEqual(item.position, 'X1:000 X2:000 Y1:050 Y2:100')

    def test_vtt_positioning(self):
        vtt = SubRipItem.from_string(self.vtt)
        self.assertEqual(vtt.position, 'D:vertical A:start L:12%')
        self.assertEqual(vtt.index, 1)
        self.assertEqual(vtt.text, 'Hello world !')

    def test_idempotence(self):
        vtt = SubRipItem.from_string(self.vtt)
        self.assertEqual(str(vtt), self.vtt)
        item = SubRipItem.from_string(self.coordinates)
        self.assertEqual(str(item), self.coordinates)

    def test_dots(self):
        self.assertEqual(SubRipItem.from_string(self.dots), self.item)

    # Bug reported in https://github.com/byroot/pysrt/issues/16
    def test_paring_error(self):
        self.assertRaises(InvalidItem, SubRipItem.from_string, '1\n'
            '00:01:00,000 -> 00:01:20,000 X1:000 X2:000 '
            'Y1:050 Y2:100\nHello world !\n')

    def test_string_index(self):
        item = SubRipItem.from_string(self.string_index)
        self.assertEquals(item.index, 'foo')
        self.assertEquals(item.text, 'Hello !')

    def test_no_index(self):
        item = SubRipItem.from_string(self.no_index)
        self.assertEquals(item.index, None)
        self.assertEquals(item.text, 'Hello world !')

    def test_junk_after_timestamp(self):
        item = SubRipItem.from_string(self.junk_after_timestamp)
        self.assertEquals(item, self.item)

if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import codecs
from datetime import time
import unittest
import random
from io import StringIO

file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.abspath(file_path))

import pysrt
from pysrt import SubRipFile, SubRipItem, SubRipTime
from pysrt.compat import str, open


class TestOpen(unittest.TestCase):

    def setUp(self):
        self.static_path = os.path.join(file_path, 'tests', 'static')
        self.utf8_path = os.path.join(self.static_path, 'utf-8.srt')
        self.windows_path = os.path.join(self.static_path, 'windows-1252.srt')
        self.invalid_path = os.path.join(self.static_path, 'invalid.srt')

    def test_utf8(self):
        self.assertEqual(len(pysrt.open(self.utf8_path)), 1332)
        self.assertEqual(pysrt.open(self.utf8_path).encoding, 'utf_8')
        self.assertRaises(UnicodeDecodeError, pysrt.open,
            self.windows_path)

    def test_windows1252(self):
        srt_file = pysrt.open(self.windows_path, encoding='windows-1252')
        self.assertEqual(len(srt_file), 1332)
        self.assertEqual(srt_file.eol, '\r\n')
        self.assertRaises(UnicodeDecodeError, pysrt.open,
            self.utf8_path, encoding='ascii')

    def test_error_handling(self):
        self.assertRaises(pysrt.Error, pysrt.open, self.invalid_path,
            error_handling=SubRipFile.ERROR_RAISE)


class TestFromString(unittest.TestCase):

    def setUp(self):
        self.static_path = os.path.join(file_path, 'tests', 'static')
        self.utf8_path = os.path.join(self.static_path, 'utf-8.srt')
        self.windows_path = os.path.join(self.static_path, 'windows-1252.srt')
        self.invalid_path = os.path.join(self.static_path, 'invalid.srt')
        self.temp_path = os.path.join(self.static_path, 'temp.srt')

    def test_utf8(self):
        unicode_content = codecs.open(self.utf8_path, encoding='utf_8').read()
        self.assertEqual(len(pysrt.from_string(unicode_content)), 1332)
        self.assertRaises(UnicodeDecodeError, open(self.windows_path).read)

    def test_windows1252(self):
        srt_string = codecs.open(self.windows_path, encoding='windows-1252').read()
        srt_file = pysrt.from_string(srt_string, encoding='windows-1252', eol='\r\n')
        self.assertEqual(len(srt_file), 1332)
        self.assertEqual(srt_file.eol, '\r\n')
        self.assertRaises(UnicodeDecodeError, pysrt.open,
            self.utf8_path, encoding='ascii')


class TestSerialization(unittest.TestCase):

    def setUp(self):
        self.static_path = os.path.join(file_path, 'tests', 'static')
        self.utf8_path = os.path.join(self.static_path, 'utf-8.srt')
        self.windows_path = os.path.join(self.static_path, 'windows-1252.srt')
        self.invalid_path = os.path.join(self.static_path, 'invalid.srt')
        self.temp_path = os.path.join(self.static_path, 'temp.srt')

    def test_compare_from_string_and_from_path(self):
        unicode_content = codecs.open(self.utf8_path, encoding='utf_8').read()
        iterator = zip(pysrt.open(self.utf8_path),
            pysrt.from_string(unicode_content))
        for file_item, string_item in iterator:
            self.assertEqual(str(file_item), str(string_item))

    def test_save(self):
        srt_file = pysrt.open(self.windows_path, encoding='windows-1252')
        srt_file.save(self.temp_path, eol='\n', encoding='utf-8')
        self.assertEqual(bytes(open(self.temp_path, 'rb').read()),
                          bytes(open(self.utf8_path, 'rb').read()))
        os.remove(self.temp_path)

    def test_eol_conversion(self):
        input_file = open(self.windows_path, 'r', encoding='windows-1252')
        input_file.read()
        self.assertEqual(input_file.newlines, '\r\n')

        srt_file = pysrt.open(self.windows_path, encoding='windows-1252')
        srt_file.save(self.temp_path, eol='\n')

        output_file = open(self.temp_path, 'r', encoding='windows-1252')
        output_file.read()
        self.assertEqual(output_file.newlines, '\n')


class TestSlice(unittest.TestCase):

    def setUp(self):
        self.file = pysrt.open(os.path.join(file_path, 'tests', 'static',
            'utf-8.srt'))

    def test_slice(self):
        self.assertEqual(len(self.file.slice(ends_before=(1, 2, 3, 4))), 872)
        self.assertEqual(len(self.file.slice(ends_after=(1, 2, 3, 4))), 460)
        self.assertEqual(len(self.file.slice(starts_before=(1, 2, 3, 4))),
                          873)
        self.assertEqual(len(self.file.slice(starts_after=(1, 2, 3, 4))),
                          459)

    def test_at(self):
        self.assertEqual(len(self.file.at((0, 0, 31, 0))), 1)
        self.assertEqual(len(self.file.at(seconds=31)), 1)


class TestZeroTimeSelection(unittest.TestCase):

    def setUp(self):
        self.file = SubRipFile([
            SubRipItem(1, start=-2000, end=-1000),
            SubRipItem(2, start=-1000, end=0),
            SubRipItem(3, start=0, end=1000),
            SubRipItem(4, start=1000, end=2000),
            SubRipItem(5, start=-1000, end=1000),
        ], path='captions.srt', encoding='utf-16', eol='\r\n')

    def assert_zero_bound(self, name, expected):
        for value in (0, {}, (), SubRipTime()):
            selected = self.file.slice(**{name: value})
            self.assertEqual([item.index for item in selected], expected)

    def test_starts_before_zero(self):
        self.assert_zero_bound('starts_before', [1, 2, 5])

    def test_starts_after_zero(self):
        self.assert_zero_bound('starts_after', [4])

    def test_ends_before_zero(self):
        self.assert_zero_bound('ends_before', [1])

    def test_ends_after_zero(self):
        self.assert_zero_bound('ends_after', [3, 4, 5])

    def test_at_integer_zero(self):
        self.assertEqual([item.index for item in self.file.at(0)], [5])

    def test_at_empty_time_values(self):
        for value in ({}, ()):
            self.assertEqual([item.index for item in self.file.at(value)], [5])

    def test_explicit_zero_takes_precedence_over_keywords(self):
        selected = self.file.at(0, seconds=2)
        self.assertEqual([item.index for item in selected], [5])

    def test_omitted_bounds(self):
        selections = (self.file.slice(), self.file.slice(starts_before=None),
                      self.file.at(), self.file.at(None))
        for selected in selections:
            self.assertEqual(list(selected), list(self.file))

    def test_nonzero_bounds_keep_strict_comparisons(self):
        selected = self.file.slice(starts_before=1000, ends_after=SubRipTime())
        self.assertEqual([item.index for item in selected], [3, 5])
        self.assertEqual(list(self.file.at(1000)), [])

    def test_selection_preserves_metadata_and_item_identity(self):
        selected = self.file.at(SubRipTime())
        self.assertTrue(selected is not self.file)
        self.assertTrue(selected[0] is self.file[4])
        self.assertEqual(selected.path, self.file.path)
        self.assertEqual(selected.encoding, self.file.encoding)
        self.assertEqual(selected.eol, self.file.eol)
        self.assertEqual(len(self.file), 5)


class TestShifting(unittest.TestCase):

    def test_shift(self):
        srt_file = SubRipFile([SubRipItem()])
        srt_file.shift(1, 1, 1, 1)
        self.assertEqual(srt_file[0].end, (1, 1, 1, 1))
        srt_file.shift(ratio=2)
        self.assertEqual(srt_file[0].end, (2, 2, 2, 2))


class TestText(unittest.TestCase):

    def test_single_item(self):
        srt_file = SubRipFile([
            SubRipItem(1, {'seconds': 1}, {'seconds': 2}, 'Hello')
        ])
        self.assertEqual(srt_file.text, 'Hello')

    def test_multiple_item(self):
        srt_file = SubRipFile([
            SubRipItem(1, {'seconds': 0}, {'seconds': 3}, 'Hello'),
            SubRipItem(1, {'seconds': 1}, {'seconds': 2}, 'World !')
        ])
        self.assertEqual(srt_file.text, 'Hello\nWorld !')


class TestDuckTyping(unittest.TestCase):

    def setUp(self):
        self.duck = SubRipFile()

    def test_act_as_list(self):
        self.assertTrue(iter(self.duck))

        def iter_over_file():
            try:
                for item in self.duck:
                    pass
            except:
                return False
            return True
        self.assertTrue(iter_over_file())
        self.assertTrue(hasattr(self.duck, '__getitem__'))
        self.assertTrue(hasattr(self.duck, '__setitem__'))
        self.assertTrue(hasattr(self.duck, '__delitem__'))


class TestEOLProperty(unittest.TestCase):

    def setUp(self):
        self.file = SubRipFile()

    def test_default_value(self):
        self.assertEqual(self.file.eol, os.linesep)
        srt_file = SubRipFile(eol='\r\n')
        self.assertEqual(srt_file.eol, '\r\n')

    def test_set_eol(self):
        self.file.eol = '\r\n'
        self.assertEqual(self.file.eol, '\r\n')


class TestCleanIndexes(unittest.TestCase):

    def setUp(self):
        self.file = pysrt.open(os.path.join(file_path, 'tests', 'static',
            'utf-8.srt'))

    def test_clean_indexes(self):
        random.shuffle(self.file)
        for item in self.file:
            item.index = random.randint(0, 1000)
        self.file.clean_indexes()
        self.assertEqual([i.index for i in self.file],
                          list(range(1, len(self.file) + 1)))
        for first, second in zip(self.file[:-1], self.file[1:]):
            self.assertTrue(first <= second)


class TestBOM(unittest.TestCase):
    "In response of issue #6 https://github.com/byroot/pysrt/issues/6"

    def setUp(self):
        self.base_path = os.path.join(file_path, 'tests', 'static')

    def __test_encoding(self, encoding):
        srt_file = pysrt.open(os.path.join(self.base_path, encoding))
        self.assertEqual(len(srt_file), 7)
        self.assertEqual(srt_file[0].index, 1)

    def test_utf8(self):
        self.__test_encoding('bom-utf-8.srt')

    def test_utf16le(self):
        self.__test_encoding('bom-utf-16-le.srt')

    def test_utf16be(self):
        self.__test_encoding('bom-utf-16-be.srt')

    def test_utf32le(self):
        self.__test_encoding('bom-utf-32-le.srt')

    def test_utf32be(self):
        self.__test_encoding('bom-utf-32-be.srt')


class TestIntegration(unittest.TestCase):
    """
    Test some borderlines features found on
    http://ale5000.altervista.org/subtitles.htm
    """

    def setUp(self):
        self.base_path = os.path.join(file_path, 'tests', 'static')

    def test_length(self):
        path = os.path.join(self.base_path, 'capability_tester.srt')
        file = pysrt.open(path)
        self.assertEqual(len(file), 37)

    def test_empty_file(self):
        file = pysrt.open('/dev/null', error_handling=SubRipFile.ERROR_RAISE)
        self.assertEqual(len(file), 0)

    def test_blank_lines(self):
        items = list(pysrt.stream(['\n'] * 20, error_handling=SubRipFile.ERROR_RAISE))
        self.assertEqual(len(items), 0)

    def test_missing_indexes(self):
        items = pysrt.open(os.path.join(self.base_path, 'no-indexes.srt'))
        self.assertEqual(len(items), 7)

if __name__ == '__main__':
    unittest.main()

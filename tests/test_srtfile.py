#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import codecs
from datetime import time
from itertools import izip
import unittest
import random
from StringIO import StringIO

file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.abspath(file_path))

import pysrt
from pysrt import SubRipFile, SubRipItem, SubRipTime
from pysrt import SUPPORT_UTF_32_LE, SUPPORT_UTF_32_BE


class TestOpen(unittest.TestCase):

    def setUp(self):
        self.static_path = os.path.join(file_path, 'tests', 'static')
        self.utf8_path = os.path.join(self.static_path, 'utf-8.srt')
        self.windows_path = os.path.join(self.static_path, 'windows-1252.srt')
        self.invalid_path = os.path.join(self.static_path, 'invalid.srt')

    def test_utf8(self):
        self.assertEquals(len(SubRipFile.open(self.utf8_path)), 1332)
        self.assertRaises(UnicodeDecodeError, SubRipFile.open,
            self.windows_path, encoding='utf_8')

    def test_windows1252(self):
        srt_file = SubRipFile.open(self.windows_path, encoding='windows-1252')
        self.assertEquals(len(srt_file), 1332)
        self.assertEquals(srt_file.eol, '\r\n')
        self.assertRaises(UnicodeDecodeError, SubRipFile.open,
            self.utf8_path, encoding='ascii')

    def test_error_handling(self):
        self.assertRaises(pysrt.Error, SubRipFile.open, self.invalid_path,
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
        self.assertEquals(len(SubRipFile.from_string(unicode_content)), 1332)
        self.assertRaises(UnicodeDecodeError, SubRipFile.from_string,
            open(self.windows_path).read())

    def test_windows1252(self):
        srt_string = codecs.open(self.windows_path, encoding='windows-1252').read()
        srt_file = SubRipFile.from_string(srt_string, encoding='windows-1252', eol='\r\n')
        self.assertEquals(len(srt_file), 1332)
        self.assertEquals(srt_file.eol, '\r\n')
        self.assertRaises(UnicodeDecodeError, SubRipFile.open,
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
        iterator = izip(SubRipFile.open(self.utf8_path),
            SubRipFile.from_string(unicode_content))
        for file_item, string_item in iterator:
            self.assertEquals(unicode(file_item), unicode(string_item))

    def test_save(self):
        srt_file = SubRipFile.open(self.windows_path, encoding='windows-1252')
        srt_file.save(self.temp_path, eol='\n', encoding='utf-8')
        self.assertEquals(open(self.temp_path, 'rb').read(),
                          open(self.utf8_path, 'rb').read())
        os.remove(self.temp_path)

    def test_eol_conversion(self):
        input_file = open(self.windows_path, 'rU')
        input_file.read()
        self.assertEquals(input_file.newlines, '\r\n')

        srt_file = SubRipFile.open(self.windows_path, encoding='windows-1252')
        srt_file.save(self.temp_path, eol='\n')

        output_file = open(self.temp_path, 'rU')
        output_file.read()
        self.assertEquals(output_file.newlines, '\n')


class TestSlice(unittest.TestCase):

    def setUp(self):
        self.file = SubRipFile.open(os.path.join(file_path, 'tests', 'static',
            'utf-8.srt'))

    def test_slice(self):
        self.assertEquals(len(self.file.slice(ends_before=(1, 2, 3, 4))), 872)
        self.assertEquals(len(self.file.slice(ends_after=(1, 2, 3, 4))), 460)
        self.assertEquals(len(self.file.slice(starts_before=(1, 2, 3, 4))),
                          873)
        self.assertEquals(len(self.file.slice(starts_after=(1, 2, 3, 4))),
                          459)


class TestShifting(unittest.TestCase):

    def test_shift(self):
        srt_file = SubRipFile([SubRipItem()])
        srt_file.shift(1, 1, 1, 1)
        self.assertEquals(srt_file[0].end, (1, 1, 1, 1))
        srt_file.shift(ratio=2)
        self.assertEquals(srt_file[0].end, (2, 2, 2, 2))


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
        self.assertEquals(self.file.eol, os.linesep)
        srt_file = SubRipFile(eol='\r\n')
        self.assertEquals(srt_file.eol, '\r\n')

    def test_set_eol(self):
        self.file.eol = '\r\n'
        self.assertEquals(self.file.eol, '\r\n')


class TestCleanIndexes(unittest.TestCase):

    def setUp(self):
        self.file = SubRipFile.open(os.path.join(file_path, 'tests', 'static',
            'utf-8.srt'))

    def test_clean_indexes(self):
        random.shuffle(self.file)
        for item in self.file:
            item.index = random.randint(0, 1000)
        self.file.clean_indexes()
        self.assertEquals([i.index for i in self.file],
                          range(1, len(self.file) + 1))
        for first, second in izip(self.file[:-1], self.file[1:]):
            self.assertTrue(first <= second)


class TestTextAtTime(unittest.TestCase):

    def setUp(self):
        self.file = SubRipFile.open(os.path.join(file_path, 'tests', 'static',
            'utf-8.srt'))

    def test_text_at_time(self):
        self.assertEquals(self.file.text_at_time(SubRipTime(0, 1, 14, 20)),
                          u'Ron Burgundy.')
        self.assertEquals(self.file.text_at_time(SubRipTime(0, 1, 16, 11)),
                          u'Ron Burgundy.')
        self.assertTrue(self.file.text_at_time(SubRipTime(0, 1, 16, 12)) is None)
        self.assertTrue(self.file.text_at_time(SubRipTime(2, 0, 0, 0)) is None)
        self.assertTrue(self.file.text_at_time(-1) is None)


class TestBOM(unittest.TestCase):
    "In response of issue #6 https://github.com/byroot/pysrt/issues/6"

    def setUp(self):
        self.base_path = os.path.join(file_path, 'tests', 'static')

    def __test_encoding(self, encoding):
        srt_file = SubRipFile.open(os.path.join(self.base_path, encoding))
        self.assertEquals(len(srt_file), 7)
        self.assertEquals(srt_file[0].index, 1)

    def test_utf8(self):
        self.__test_encoding('bom-utf-8.srt')

    def test_utf16le(self):
        self.__test_encoding('bom-utf-16-le.srt')

    def test_utf16be(self):
        self.__test_encoding('bom-utf-16-be.srt')

    if SUPPORT_UTF_32_LE:
        def test_utf32le(self):
            self.__test_encoding('bom-utf-32-le.srt')

    if SUPPORT_UTF_32_BE:
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
        file = SubRipFile.open(path)
        self.assertEquals(len(file), 37)

    def test_empty_file(self):
        file = SubRipFile.open('/dev/null', error_handling=SubRipFile.ERROR_RAISE)
        self.assertEquals(len(file), 0)

    def test_file_with_empty_items(self):
        path = os.path.join(self.base_path, 'empty.srt')
        file = SubRipFile.open(path)
        self.assertEquals(len(file), 7)

    def test_blank_lines(self):
        items = list(SubRipFile.stream([u'\n'] * 20, error_handling=SubRipFile.ERROR_RAISE))
        self.assertEquals(len(items), 0)

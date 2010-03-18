#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from datetime import time
from itertools import izip
import unittest
import random
from StringIO import StringIO

file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.abspath(file_path))

from pysrt import SubRipFile, SubRipItem, SubRipTime, InvalidItem


class TestOpen(unittest.TestCase):

    def setUp(self):
        self.static_path = os.path.join(file_path, 'tests', 'static')
        self.utf8_path = os.path.join(self.static_path, 'utf-8.srt')
        self.windows_path = os.path.join(self.static_path, 'windows-1252.srt')
        self.invalid_path = os.path.join(self.static_path, 'invalid.srt')

    def test_utf8(self):
        self.assertEquals(len(SubRipFile.open(self.utf8_path)), 1332)
        self.assertRaises(UnicodeDecodeError, SubRipFile.open,
            self.windows_path)

    def test_windows1252(self):
        srt_file = SubRipFile.open(self.windows_path, encoding='windows-1252')
        self.assertEquals(len(srt_file), 1332)
        self.assertEquals(srt_file.eol, '\r\n')
        self.assertRaises(UnicodeDecodeError, SubRipFile.open,
            self.utf8_path, encoding='ascii')

    def test_error_handling(self):
        self.assertRaises(InvalidItem, SubRipFile.open, self.invalid_path,
            error_handling=SubRipFile.ERROR_RAISE)
        try:
            SubRipFile.open(self.invalid_path,
                error_handling=SubRipFile.ERROR_RAISE)
        except Exception, exc:
            self.assertEquals(exc.args, (
                self.invalid_path, 3,
                u'1\n00:00:01 --> 00:00:10\nThis subtitle is invalid\n'))

        sys.stderr = StringIO()
        srt_file = SubRipFile.open(self.invalid_path,
            error_handling=SubRipFile.ERROR_LOG)
        sys.stderr.seek(0)
        self.assertEquals(sys.stderr.read(), 'PySRT-InvalidItem(%s:3): \n1\n00:'
            '00:01 --> 00:00:10\nThis subtitle is invalid\n\nPySRT-InvalidItem('
            '%s:4): \n\n' % ((self.invalid_path,) * 2))


class TestSerialization(unittest.TestCase):

    def setUp(self):
        self.static_path = os.path.join(file_path, 'tests', 'static')
        self.utf8_path = os.path.join(self.static_path, 'utf-8.srt')
        self.windows_path = os.path.join(self.static_path, 'windows-1252.srt')
        self.invalid_path = os.path.join(self.static_path, 'invalid.srt')
        self.temp_path = os.path.join(self.static_path, 'temp.srt')

    def test_compare_from_string_and_from_path(self):
        iterator = izip(SubRipFile.open(self.utf8_path),
            SubRipFile.from_string(open(self.utf8_path).read()))
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

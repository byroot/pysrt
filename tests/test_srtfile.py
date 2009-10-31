#!/usr/bin/env python

import os
import sys
from datetime import time
from itertools import izip
import unittest
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
        self.assertEquals(len(SubRipFile.open(self.windows_path,
            encoding='windows-1252')), 1332)
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
        self.assertEquals(sys.stderr.read(), 'PySRT-InvalidItem(/Users/byroot'
            u'/workspace/pysrt/tests/static/invalid.srt:3): \n1\n00:00:01 -->'
            u' 00:00:10\nThis subtitle is invalid\n\nPySRT-InvalidItem(/Users'
            u'/byroot/workspace/pysrt/tests/static/invalid.srt:4): \n\n')


class TestSerialization(unittest.TestCase):

    def setUp(self):
        self.static_path = os.path.join(file_path, 'tests', 'static')
        self.utf8_path = os.path.join(self.static_path, 'utf-8.srt')
        self.windows_path = os.path.join(self.static_path, 'windows-1252.srt')
        self.invalid_path = os.path.join(self.static_path, 'invalid.srt')

    def test_compare_from_string_and_from_path(self):
        iterator = izip(SubRipFile.open(self.utf8_path),
            SubRipFile.from_string(open(self.utf8_path).read()))
        for file_item, string_item in iterator:
            self.assertEquals(unicode(file_item), unicode(string_item))


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

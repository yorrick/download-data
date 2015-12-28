# -*- coding: utf-8 -*-
from extract.argument_parsing import *
from unittest import TestCase


class TestArgumentParsing(TestCase):

    def test_parse_argv_1(self):
        params = parse_argv(["script_name.py", "--detect-downloads-above", "500", "data/file1.log", "data/file2.log"])
        self.assertEquals(params.log_files, ["data/file1.log", "data/file2.log"])
        self.assertEquals(params.detect_downloads_above, 500)

    def test_parse_argv_2(self):
        params = parse_argv(["script_name.py", "data/file1.log", "data/file2.log"])
        self.assertEquals(params.log_files, ["data/file1.log", "data/file2.log"])
        self.assertFalse(params.detect_downloads_above, None)

# -*- coding: utf-8 -*-
from extract.argument_parsing import *
from unittest import TestCase


class TestArgumentParsing(TestCase):

    def test_parse_argv(self):
        params = parse_argv(["script_name.py", "--debug", "--processes", "7", "data/file1.log", "data/file2.log"])
        self.assertEquals(params.log_files, ["data/file1.log", "data/file2.log"])
        self.assertTrue(params.debug)
        self.assertEquals(params.processes, 7)

    def test_parse_argv_default_args(self):
        params = parse_argv(["script_name.py", "data/file1.log", "data/file2.log"])
        self.assertEquals(params.log_files, ["data/file1.log", "data/file2.log"])
        self.assertFalse(params.debug)
        self.assertEquals(params.processes, 4)

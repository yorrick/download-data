# -*- coding: utf-8 -*-
from extract.argument_parsing import *
from unittest import TestCase


class TestArgumentParsing(TestCase):

    def test_parse_argv_1(self):
        params = parse_argv(["script_name.py", "data/file1.log", "data/file2.log"])
        self.assertEquals(params.log_files, ["data/file1.log", "data/file2.log"])

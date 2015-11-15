# -*- coding: utf-8 -*-
from extract.common import *
from unittest import TestCase


class TestCommon(TestCase):

    def test_build_result_log(self):
        result_log = build_result_log("toto.log", 100, 55, 53, 10)
        self.assertEqual(result_log, "toto.log: Total: 100 => Interesting: 55 (55.00%) => Extracted: 53 (53.00%) => Downloads: 10 (10.00%)")

    def test_parse_argv_1(self):
        params = parse_argv(["script_name.py", "--detect-downloads-above", "500", "data/file1.log", "data/file2.log"])
        self.assertEquals(params.log_files, ["data/file1.log", "data/file2.log"])
        self.assertEquals(params.detect_downloads_above, 500)

    def test_parse_argv_2(self):
        params = parse_argv(["script_name.py", "data/file1.log", "data/file2.log"])
        self.assertEquals(params.log_files, ["data/file1.log", "data/file2.log"])
        self.assertFalse(params.detect_downloads_above, None)

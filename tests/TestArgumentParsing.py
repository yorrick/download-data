# -*- coding: utf-8 -*-
from extract.argument_parsing import *
from unittest import TestCase


class TestArgumentParsing(TestCase):

    def test_parse_argv(self):
        params = parse_argv([
            "script_name.py", "--debug", "--keep-robots",
            "--processes", "7",
            "--print-stats-for-ip", "222.222.222.222",
            "data/file1.log", "data/file2.log"])
        self.assertEquals(params.log_files, ["data/file1.log", "data/file2.log"])
        self.assertTrue(params.debug)
        self.assertTrue(params.keep_robots)
        self.assertEquals(params.processes, 7)
        self.assertEquals(params.print_stats_for_ip, "222.222.222.222")

    def test_parse_argv_default_args(self):
        params = parse_argv(["script_name.py", "data/file1.log", "data/file2.log"])
        self.assertEquals(params.log_files, ["data/file1.log", "data/file2.log"])
        self.assertFalse(params.debug)
        self.assertFalse(params.keep_robots)
        self.assertEquals(params.processes, 4)

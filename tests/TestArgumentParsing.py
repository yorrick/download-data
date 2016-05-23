# -*- coding: utf-8 -*-
from extract.argument_parsing import *
from unittest import TestCase


class TestArgumentParsing(TestCase):

    def test_parse_argv(self):
        params = parse_argv([
            "script_name.py", "--debug", "--keep-robots",
            "--processes", "7",
            "--print-stats-for-ip", "222.222.222.222",
            "/tmp/", "/tmp/"])
        self.assertEquals(params.source_dir, "/tmp/")
        self.assertEquals(params.output_dir, "/tmp/")
        self.assertTrue(params.debug)
        self.assertTrue(params.keep_robots)
        self.assertEquals(params.processes, 7)
        self.assertEquals(params.print_stats_for_ip, "222.222.222.222")

    def test_parse_argv_default_args(self):
        params = parse_argv(["script_name.py", "/tmp/", "/tmp/"])
        self.assertFalse(params.debug)
        self.assertFalse(params.keep_robots)
        self.assertEquals(params.processes, 4)

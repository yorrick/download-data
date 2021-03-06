# -*- coding: utf-8 -*-
from extract.common import *
from unittest import TestCase
from os import path


BASE_DIR = path.dirname(path.abspath(__file__))


class TestCommon(TestCase):

    def test_build_result_log(self):
        result_log = build_result_log("toto.log", 100, 55, 53, 10)
        self.assertEqual(result_log, "toto.log: Total: 100 => parsable: 55 (55.00%) => download: 53 (53.00%) => considered_human: 10 (10.00%)")

    def test_get_files(self):
        self.assertEqual(get_files(BASE_DIR, suffix = ".log"), {"test-log.log", "test-log-empty.log"})

    def test_get_files_with_filter(self):
        self.assertEqual(get_files(BASE_DIR, suffix = ".log", filter=non_emtpy), {"test-log.log"})

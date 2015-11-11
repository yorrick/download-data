# -*- coding: utf-8 -*-
from extract.common import *
from unittest import TestCase


class TestCommon(TestCase):

    def test_build_result_log(self):
        result_log = build_result_log("toto.log", 100, 55, 53, 10, {})
        self.assertEqual(result_log, "toto.log: Total: 100 => Interesting: 55 (55.00%) => Extracted: 53 (53.00%) => Downloads: 10 (10.00%)\nTop ips that downloaded the most:\n")

# -*- coding: utf-8 -*-
from extract.journals import *
from unittest import TestCase
from os import path

BASE_DIR = path.dirname(path.abspath(__file__))


class TestExtract(TestCase):

    def test_build_journal_referential(self):
        referential = build_journal_referential(path.join(BASE_DIR, "test-journals.json"))
        self.assertEquals(len(referential.journals), 3)
        self.assertEquals(len(referential.journal_names), 4)
        self.assertEquals(referential.journal_names, {
            "ac": "crimino",
            "crimino": "crimino",
            "acadiensis": "acadiensis",
            "ae": "ae",
        })

    def test_build_full_referential(self):
        # tests that no fail happens
        build_journal_referential("journals.json")
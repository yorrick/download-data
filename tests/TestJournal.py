# -*- coding: utf-8 -*-
from extract.journals import *
from unittest import TestCase
from os import path

BASE_DIR = path.dirname(path.abspath(__file__))


class TestExtract(TestCase):

    def test_journal_referential(self):
        referential = build_journal_referential(path.join(BASE_DIR, "test-journals.json"))
        self.assertEquals(len(referential.journals), 3)
        self.assertEquals(len(referential._journal_names), 4)

        self.assertEquals(referential.get_journal_id("ae"), "ae")
        self.assertEquals(referential.get_journal_id("toto"), "toto")
        self.assertEquals(referential.get_journal_id("ac"), "crimino")

        self.assertEquals(referential.get_journal_first_domain("ae"), "economie")
        self.assertEquals(referential.get_journal_first_domain("crimino"), "droit")
        self.assertEquals(referential.get_journal_first_domain("toto"), "")

        self.assertTrue(referential.is_journal_full_oa("ae"))
        self.assertFalse(referential.is_journal_full_oa("crimino"))
        self.assertEquals(referential.is_journal_full_oa("toto"), "")

    def test_build_full_referential(self):
        # tests that no fail happens
        build_journal_referential("journals.json")
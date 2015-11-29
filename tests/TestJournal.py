# -*- coding: utf-8 -*-
from extract.journals import *
from unittest import TestCase
from os import path

BASE_DIR = path.dirname(path.abspath(__file__))


class TestExtract(TestCase):

    def test_build_journal_referential(self):
        journals = build_journal_referential(path.join(BASE_DIR, "journals.json"))

    def test_build_full_referential(self):
        # tests that no fail happens
        build_journal_referential("journals.json")
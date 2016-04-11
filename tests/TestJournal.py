# -*- coding: utf-8 -*-
from extract.journals import *
from unittest import TestCase
from os import path

BASE_DIR = path.dirname(path.abspath(__file__))


class TestJournal(TestCase):

    def test_journal_referential(self):
        referential = build_journal_referential(path.join(BASE_DIR, "test-journals.json"))
        self.assertEquals(len(referential.journals), 3)
        self.assertEquals(len(referential._journal_names), 4)

        self.assertEquals(referential.get_journal_id("ae"), "ae")
        self.assertEquals(referential.get_journal_id("toto"), "toto")
        self.assertEquals(referential.get_journal_id("ac"), "crimino")

        self.assertEquals(referential.get_journal_general_discipline("ae").main, "Social Sciences and Humanities")
        self.assertEquals(referential.get_journal_general_discipline("ae").fr, "Sciences sociales et humaines")
        self.assertEquals(referential.get_journal_general_discipline("toto"), None)
        self.assertEquals(referential.get_journal_discipline("acadiensis").main, "Humanities")
        self.assertEquals(referential.get_journal_discipline("acadiensis").fr, "Humanites")
        self.assertEquals(referential.get_journal_discipline("toto"), None)
        self.assertEquals(referential.get_journal_speciality("crimino").main, "Criminology")
        self.assertEquals(referential.get_journal_speciality("crimino").fr, "Criminologie")
        self.assertEquals(referential.get_journal_speciality("toto"), None)

        self.assertTrue(referential.is_journal_full_oa("ae"))
        self.assertFalse(referential.is_journal_full_oa("crimino"))
        self.assertEquals(referential.is_journal_full_oa("toto"), "")

    def test_build_full_referential(self):
        # tests that no fail happens
        build_journal_referential("journals.json")

    def test_to_csv_rows(self):
        journals = JournalReferential([
                {
                    "id": "crimino",
                    "names": [
                        {"url_name": "ac", "full_name": "Acta Criminologica", "start_year": 1968, "stop_year": 1974},
                        {"url_name": "crimino", "full_name": "Criminologie", "start_year": 1975}
                    ],
                    "general_discipline_fr": "Sciences sociales et humaines",
                    "general_discipline": "Social Sciences and Humanities",
                    "discipline_fr": "Sciences sociales",
                    "discipline": "Social Sciences",
                    "speciality_fr": "Criminologie",
                    "speciality": "Criminology",
                    "full_oa": False
                }
            ])

        print(list(journals.to_csv_rows()))

        self.assertEquals(list(journals.to_csv_rows()), [
            [
                "crimino",
                "Social Sciences and Humanities",
                "Sciences sociales et humaines",
                "Social Sciences",
                "Sciences sociales",
                "Criminology",
                "Criminologie",
                False
            ]
        ])

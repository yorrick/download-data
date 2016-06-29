# -*- coding: utf-8 -*-
from __future__ import print_function
import codecs
import json


class Translation():
    def __init__(self, main, fr):
        self.main = main
        self.fr = fr


def build_reverse_dict(iterable, key_extractor, value_extractor = lambda x: x):
    result = {}

    for item in iterable:
        key = key_extractor(item)
        value = value_extractor(item)

        # support for multi valuated keys
        if isinstance(key, list):
            for k in key:
                result[k] = value
        else:
            result[key] = value

    return result


class JournalReferential():

    def __init__(self, journals):
        self.journals = journals
        self._journal_names = build_reverse_dict(self.journals, _get_journal_names, _get_journal_id)
        self._journal_general_discipline = build_reverse_dict(self.journals, _get_journal_id, _get_journal_general_discipline)
        self._journal_discipline = build_reverse_dict(self.journals, _get_journal_id, _get_journal_discipline)
        self._journal_speciality = build_reverse_dict(self.journals, _get_journal_id, _get_journal_speciality)
        self._journal_other_ids = build_reverse_dict(self.journals, _get_journal_id, _get_journal_other_ids)
        self._journal_full_oa = build_reverse_dict(self.journals, _get_journal_id, _get_journal_full_oa)
        self._full_text_html_ranges = build_reverse_dict(self.journals, _get_journal_id, _get_full_text_html_ranges)

    def get_journal_id(self, journal_name):
        return self._journal_names.get(journal_name, journal_name)


    def get_journal_general_discipline(self, journal_id):
        return self._journal_general_discipline.get(journal_id, None)

    def get_journal_discipline(self, journal_id):
        return self._journal_discipline.get(journal_id, None)

    def get_journal_speciality(self, journal_id):
        return self._journal_speciality.get(journal_id, None)

    def get_journal_other_ids(self, journal_id):
        return self._journal_other_ids.get(journal_id, None)

    def is_html_a_download(self, journal_id, year):
        return any(year >= start and year <= stop for (start, stop) in self._full_text_html_ranges.get(journal_id, []))

    def is_journal_full_oa(self, journal_id):
        return self._journal_full_oa.get(journal_id, "")

    def to_journal_csv_rows(self):
        return (_to_csv_row(j) for j in self.journals)


def _to_csv_row(journal):
    gen_disc = _get_journal_general_discipline(journal)
    disc = _get_journal_discipline(journal)
    spe = _get_journal_speciality(journal)

    return [_get_journal_id(journal)[:20]] + \
             ([gen_disc.main[:50], gen_disc.fr[:50]] if gen_disc else ['', '']) + \
             ([disc.main[:50], disc.fr[:50]] if disc else ['', '']) + \
             ([spe.main[:50], spe.fr[:50]] if spe else ['', '']) + \
             ([_get_journal_full_oa(journal)])


def build_journal_referential(file_path):
    with codecs.open(file_path, "r", "utf-8") as journal_file:
        return JournalReferential(json.load(journal_file))


def _get_journal_names(journal):
    return [name["url_name"].lower() for name in journal["names"]]


def _get_journal_general_discipline(journal):
    return Translation(journal["general_discipline"], journal["general_discipline_fr"])


def _get_journal_discipline(journal):
    return Translation(journal["discipline"], journal["discipline_fr"])


def _get_journal_speciality(journal):
    return Translation(journal["speciality"], journal["speciality_fr"])


def _get_journal_other_ids(journal):
    return journal["other_ids"]

def _get_journal_full_oa(journal):
    return journal["full_oa"]

def _get_journal_id(journal):
    return journal["id"].lower()

def _get_full_text_html_ranges(journal):
    return [_get_range(r) for r in journal["full_text_html"]]

def _get_range(range):
    start = range["start_year"]
    stop = range.get("stop_year", 9999)

    return (start, stop)




EMPTY_REFERENTIAL = JournalReferential([])

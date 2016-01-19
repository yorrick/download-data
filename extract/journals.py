# -*- coding: utf-8 -*-
from __future__ import print_function
import codecs
import json


class JournalReferential():

    def __init__(self, journals):
        self.journals = journals
        self._journal_names = self.build_reverse_dict(self.journals, _get_journal_names, _get_journal_id)
        self._journal_domains = self.build_reverse_dict(self.journals, _get_journal_id, _get_journal_domains)
        self._journal_full_oa = self.build_reverse_dict(self.journals, _get_journal_id, _get_journal_full_oa)

    @classmethod
    def build_reverse_dict(cls, iterable, key_extractor, value_extractor = lambda x: x):
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

    def get_journal_id(self, journal_name):
        return self._journal_names.get(journal_name, journal_name)

    def get_journal_first_domain(self, journal_id):
        return self._journal_domains.get(journal_id, [''])[0]

    def is_journal_full_oa(self, journal_id):
        return self._journal_full_oa.get(journal_id, '')

    def to_csv_rows(self):
        return (
            [_get_journal_id(j), _get_journal_full_oa(j)]
            for j in self.journals
        )


def build_journal_referential(file_path):
    with codecs.open(file_path, "r", "utf-8") as journal_file:
        return JournalReferential(json.load(journal_file))


def _get_journal_names(journal):
    return [name["url_name"].lower() for name in journal["names"]]


def _get_journal_domains(journal):
    return [domain.lower() for domain in journal["domains"]]


def _get_journal_full_oa(journal):
    return journal["full_oa"]


def _get_journal_id(journal):
    return journal["id"].lower()


EMPTY_REFERENTIAL = JournalReferential([])

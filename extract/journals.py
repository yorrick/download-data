# -*- coding: utf-8 -*-
from __future__ import print_function
import codecs
import json


class JournalReferential():

    def __init__(self, journals):
        self.journals = journals
        self.journal_names = self.build_reverse_dict(self.journals, _get_journal_names, _get_journal_id)

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

        return result


def build_journal_referential(file_path):
    with codecs.open(file_path, "r", "utf-8") as journal_file:
        return JournalReferential(json.load(journal_file))


def _get_journal_names(journal):
    return [name["url_name"] for name in journal["names"]]

def _get_journal_id(journal):
    return journal["id"]


EMPTY_REFERENTIAL = JournalReferential([])

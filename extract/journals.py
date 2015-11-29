# -*- coding: utf-8 -*-
from __future__ import print_function
import codecs
import json


class JournalReferential():

    def __init__(self):
        pass


def build_journal_referential(file_path):
    with codecs.open(file_path, "r", "utf-8") as journal_file:
        return json.load(journal_file)

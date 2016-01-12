# -*- coding: utf-8 -*-
from extract.extract import *
from extract.activity_tracker import *
from datetime import datetime
from unittest import TestCase
from os import path

BASE_DIR = path.dirname(path.abspath(__file__))


class TestExtract(TestCase):

    def test_download_flags_for_article_download(self):
        record = Record(
            get_montreal_time(datetime(2015, 3, 3, 23, 59, 55)),
            "202.112.50.77",
            "GET",
            "/revue/ltp/1987/v43/n3/400333ar.pdf",
            "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)",
            "202.112.50.77",
            "-",
            200,
        )

        self.assertFalse(record.is_css_download)
        self.assertFalse(record.is_javascript_download)
        self.assertFalse(record.is_image_download)
        self.assertTrue(record.is_article_download)

    def test_download_flags_for_image_download(self):
        record = Record(
            get_montreal_time(datetime(2015, 3, 3, 23, 59, 55)),
            "202.112.50.77",
            "GET",
            "toto.png",
            "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)",
            "202.112.50.77",
            "-",
            200,
        )

        self.assertFalse(record.is_css_download)
        self.assertFalse(record.is_javascript_download)
        self.assertTrue(record.is_image_download)
        self.assertFalse(record.is_article_download)

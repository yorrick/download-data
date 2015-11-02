# -*- coding: utf-8 -*-
from extract.extract import *
from datetime import datetime
from unittest import TestCase
from os import path

BASE_DIR = path.dirname(path.abspath(__file__))


class TestExtract(TestCase):

    def test_line_extract_1(self):
        line = """2015-03-03 23:59:55 52.16.55.221 GET /revue/JCHA/1995/v6/n1/031091ar.pdf HTTP/1.1 - 80 - 52.16.55.221 "curl/7.35.0" "-" 200 1306973"""
        record = extract(line)

        self.assertEqual(record.timestamp, datetime(2015, 3, 3, 23, 59, 55))
        self.assertEqual(record.first_ip, "52.16.55.221")
        self.assertEqual(record.http_method, "GET")
        self.assertEqual(record.url, "/revue/JCHA/1995/v6/n1/031091ar.pdf")
        self.assertEqual(record.second_ip, "52.16.55.221")
        self.assertEqual(record.user_agent, "curl/7.35.0")
        self.assertEqual(record.referer, "-")
        self.assertEqual(record.http_response_code, 200)


    def test_line_extract_2(self):
        line = """2015-03-04 02:17:29 100.43.91.4 GET / HTTP/1.1 - 80 - 100.43.91.4 "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)" "-" 200 6387"""
        record = extract(line)

        self.assertEqual(record.timestamp, datetime(2015, 3, 4, 2, 17, 29))
        self.assertEqual(record.first_ip, "100.43.91.4")
        self.assertEqual(record.http_method, "GET")
        self.assertEqual(record.url, "/")
        self.assertEqual(record.second_ip, "100.43.91.4")
        self.assertEqual(record.user_agent, "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)")
        self.assertEqual(record.referer, "-")
        self.assertEqual(record.http_response_code, 200)


    def test_line_extract_3(self):
        line = """2015-03-04 00:29:36 222.33.68.117 GET / - 80 - 222.33.68.117 "-" "-" 400 460"""
        record = extract(line)

        self.assertEqual(record.timestamp, datetime(2015, 3, 4, 0, 29, 36))
        self.assertEqual(record.first_ip, "222.33.68.117")
        self.assertEqual(record.http_method, "GET")
        self.assertEqual(record.second_ip, "222.33.68.117")
        self.assertEqual(record.url, "/")
        self.assertEqual(record.user_agent, "-")
        self.assertEqual(record.referer, "-")
        self.assertEqual(record.http_response_code, 400)


    def test_line_extract_4(self):
        line = """2015-03-04 03:13:51 125.122.116.68 POST / HTTP/1.1 - 80 - 125.122.116.68 "" "-" 200 6387"""
        record = extract(line)

        self.assertEqual(record.timestamp, datetime(2015, 3, 4, 3, 13, 51))
        self.assertEqual(record.first_ip, "125.122.116.68")
        self.assertEqual(record.http_method, "POST")
        self.assertEqual(record.second_ip, "125.122.116.68")
        self.assertEqual(record.url, "/")
        self.assertEqual(record.user_agent, "")
        self.assertEqual(record.referer, "-")
        self.assertEqual(record.http_response_code, 200)

    def test_line_extract_5(self):
        """Space in url, at the end"""
        line = """2015-03-04 05:45:05 113.225.67.107 POST /F/AAH5hZjAp4REK7En3PgjyTX_  HTTP/1.1 - 80 - 113.225.67.107 "-" "-" 404 1385"""
        record = extract(line)
        self.assertIsNone(record)

    def test_line_extract_6(self):
        """Space in url"""
        line = """2015-03-04 00:31:30 209.240.101.210 GET /bitstream/003422dd/1/Bulletin_CIRPEE_Winter 2011.pdf HTTP/1.1 - 80 - 209.240.101.210 "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:35.0) Gecko/20100101 Firefox/35.0" "https://depot.erudit.org/" 404 7340"""
        record = extract(line)
        self.assertIsNone(record)

    def test_line_extract_7(self):
        """No GET, or no URL"""
        line = """2015-03-04 04:12:09 202.112.50.77 quit - 80 - 202.112.50.77 "-" "-" 200 6387"""
        record = extract(line)
        self.assertIsNone(record)

    def test_get_lines(self):
        lines = get_lines(path.join(BASE_DIR, "test-log.log"))
        self.assertEquals(len(list(lines)), 4)

    def test_non_interesting_line_are_discarded(self):
        line = """2015-03-04 04:12:09 202.112.50.77 quit - 80 - 202.112.50.77 "-" "-" 200 6387"""
        self.assertFalse(interesting_line(line))

    def test_interesting_line_are_kept(self):
        line = """2015-03-03 23:59:55 52.16.55.221 GET  /revue/JCHA/1995/v6/n1/031091ar.pdf HTTP/1.1 - 80 - 52.16.55.221 "curl/7.35.0" "-" 200 1306973"""
        self.assertTrue(interesting_line(line))

    def test_record_is_download(self):
        record = Record(
            datetime(2015, 3, 3, 23, 59, 55),
            "202.112.50.77",
            "GET",
            "/revue/JCHA/1995/v6/n1/031091ar.pdf",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:35.0) Gecko/20100101 Firefox/35.0",
            "202.112.50.77",
            "-",
            200,
        )

        self.assertTrue(is_pdf_download(record))

    def test_record_is_not_download(self):
        record = Record(
            datetime(2015, 3, 3, 23, 59, 55),
            "202.112.50.77",
            "GET",
            "/revue/JCHA/1995/v6/n1/031091ar.pdf",
            "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)",
            "202.112.50.77",
            "-",
            200,
        )

        self.assertFalse(is_pdf_download(record))

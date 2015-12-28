# -*- coding: utf-8 -*-
from extract.extract import *
from extract.journals import *
from datetime import datetime
from unittest import TestCase
from os import path

BASE_DIR = path.dirname(path.abspath(__file__))


class TestExtract(TestCase):

    def test_line_extract_1(self):

        line = """2015-03-03 23:59:55 52.16.55.221 GET /revue/ac/1995/v6/n1/031091ar.pdf HTTP/1.1 - 80 - 52.16.55.221 "curl/7.35.0" "http://www.bing.com/search?q=compare%20christ%20and%20bonhoeffer&pc=cosp&ptag=A0F73A159EF&form=CONBDF&conlogo=CT3210127" 200 1306973"""
        record = extract(line)

        self.assertEqual(record.timestamp, get_montreal_time(datetime(2015, 3, 3, 23, 59, 55)))
        self.assertEqual(record.time, "2015-03-03 23:59:55")
        self.assertEqual(record.date, "2015-03-03")
        self.assertEqual(record.year, 2015)
        self.assertEqual(record.hour, 23)

        self.assertEqual(record.local_time, "2015-03-04 04:59:55")
        self.assertEqual(record.local_date, "2015-03-04")
        self.assertEqual(record.local_year, 2015)
        self.assertEqual(record.local_hour, 4)

        self.assertEqual(record.referer, "http://www.bing.com/search?q=compare%20christ%20and%20bonhoeffer&pc=cosp&ptag=A0F73A159EF&form=CONBDF&conlogo=CT3210127")
        self.assertEqual(record.referer_host, "www.bing.com")

        self.assertEqual(record.user_ip, "52.16.55.221")
        self.assertEqual(record.continent, "EU")
        self.assertEqual(record.country, "Ireland")
        self.assertEqual(record.geo_coordinates, "53.3331, -6.2489")
        self.assertEqual(record.timezone, "Europe/Dublin")

        self.assertEqual(record.proxy_ip, "52.16.55.221")
        self.assertEqual(record.http_method, "GET")
        self.assertEqual(record.url, "/revue/ac/1995/v6/n1/031091ar.pdf")

        self.assertEqual(record.journal_name, "ac")
        # self.assertEqual(record.journal_domain, "droit")
        self.assertEqual(record.publication_year, 1995)
        self.assertEqual(record.volume, "v6")
        self.assertEqual(record.issue, "n1")
        self.assertEqual(record.article_id, "031091")

        self.assertEqual(record.raw_user_agent, "curl/7.35.0")
        self.assertEqual(record.browser, "Other")
        self.assertEqual(record.os, "Other")
        self.assertEqual(record.device, "Other")
        self.assertFalse(record.is_bot)

        self.assertEqual(record.http_response_code, 200)

        self.assertEqual(record.age, 20)
        self.assertFalse(record.embargo)


    def test_line_extract_2(self):
        line = """2015-03-04 02:17:29 100.43.91.4 GET /revue/JCHA/2014/v6/n1/031091ar.pdf HTTP/1.1 - 80 - 100.43.91.4 "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)" "-" 200 6387"""
        record = extract(line)

        self.assertEqual(record.timestamp, get_montreal_time(datetime(2015, 3, 4, 2, 17, 29)))
        self.assertEqual(record.proxy_ip, "100.43.91.4")
        self.assertEqual(record.http_method, "GET")
        self.assertEqual(record.url, "/revue/JCHA/2014/v6/n1/031091ar.pdf")

        self.assertEqual(record.user_ip, "100.43.91.4")
        self.assertEqual(record.country, "United States of America")
        self.assertEqual(record.continent, "NA")
        self.assertEqual(record.timezone, "America/Los_Angeles")
        self.assertEqual(record.geo_coordinates, "37.4135, -122.1312")

        self.assertEqual(record.journal_name, "jcha")
        # self.assertEqual(record.journal_domain, "")

        self.assertEqual(record.raw_user_agent, "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)")
        self.assertEqual(record.browser, "YandexBot")
        self.assertEqual(record.os, "Other")
        self.assertEqual(record.device, "Spider")
        self.assertTrue(record.is_bot)

        self.assertEqual(record.referer, "")
        self.assertEqual(record.http_response_code, 200)

        self.assertEqual(record.age, 1)
        self.assertTrue(record.embargo)


    def test_line_extract_3(self):
        line = """2015-03-04 00:29:36 222.33.68.117 GET /revue/JCHA/2015/v6/n1/031091ar.pdf - 80 - 222.33.68.117 "-" "-" 400 460"""
        record = extract(line)

        self.assertEqual(record.timestamp, get_montreal_time(datetime(2015, 3, 4, 0, 29, 36)))
        self.assertEqual(record.proxy_ip, "222.33.68.117")
        self.assertEqual(record.http_method, "GET")

        self.assertEqual(record.user_ip, "222.33.68.117")
        self.assertEqual(record.country, "China")
        self.assertEqual(record.continent, "AS")
        self.assertEqual(record.timezone, "Asia/Shanghai")
        self.assertEqual(record.geo_coordinates, "39.9289, 116.3883")

        self.assertEqual(record.url, "/revue/JCHA/2015/v6/n1/031091ar.pdf")

        self.assertEqual(record.raw_user_agent, "-")
        self.assertEqual(record.browser, "Other")
        self.assertEqual(record.os, "Other")
        self.assertEqual(record.device, "Other")
        self.assertFalse(record.is_bot)

        self.assertEqual(record.referer, "")
        self.assertEqual(record.http_response_code, 400)

        self.assertEqual(record.age, 0)
        self.assertTrue(record.embargo)


    def test_line_extract_4(self):
        line = """2015-03-04 03:13:51 125.122.116.68 POST /revue/JCHA/1995/v6/n1/031091ar.pdf HTTP/1.1 - 80 - 125.122.116.68 "" "-" 200 6387"""
        record = extract(line)

        self.assertEqual(record.timestamp, get_montreal_time(datetime(2015, 3, 4, 3, 13, 51)))
        self.assertEqual(record.proxy_ip, "125.122.116.68")
        self.assertEqual(record.http_method, "POST")

        self.assertEqual(record.user_ip, "125.122.116.68")
        self.assertEqual(record.country, "China")
        self.assertEqual(record.continent, "AS")
        self.assertEqual(record.timezone, "Asia/Shanghai")
        self.assertEqual(record.geo_coordinates, "30.2936, 120.1614")

        self.assertEqual(record.url, "/revue/JCHA/1995/v6/n1/031091ar.pdf")

        self.assertEqual(record.raw_user_agent, "")
        self.assertEqual(record.browser, "")
        self.assertEqual(record.os, "")
        self.assertEqual(record.device, "")
        self.assertFalse(record.is_bot)

        self.assertEqual(record.referer, "")
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

    def test_line_extract_8(self):
        """URL does not match"""
        line = """2015-03-03 23:59:55 52.16.55.221 GET /favico HTTP/1.1 - 80 - 52.16.55.221 "curl/7.35.0" "-" 200 1306973"""
        record = extract(line)
        self.assertIsNone(record)

    def test_get_lines(self):
        lines = get_lines(path.join(BASE_DIR, "test-log.log"))
        self.assertEquals(len(list(lines)), 4)

    def test_non_interesting_lines_are_discarded(self):
        line = """2015-03-04 04:12:09 202.112.50.77 quit - 80 - 202.112.50.77 "-" "-" 200 6387"""
        self.assertFalse(interesting_line(line))

    def test_interesting_lines_are_kept(self):
        line = """2015-03-03 23:59:55 52.16.55.221 GET  /revue/JCHA/1995/v6/n1/031091ar.pdf HTTP/1.1 - 80 - 52.16.55.221 "curl/7.35.0" "-" 200 1306973"""
        self.assertTrue(interesting_line(line))

    def test_html_lines_are_kept(self):
        line = """2015-03-03 23:59:55 52.16.55.221 GET  /revue/JCHA/1995/v6/n1/031091ar.html HTTP/1.1 - 80 - 52.16.55.221 "curl/7.35.0" "-" 200 1306973"""
        self.assertTrue(interesting_line(line))

    def test_record_is_download(self):
        record = Record(
            get_montreal_time(datetime(2015, 3, 3, 23, 59, 55)),
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
            get_montreal_time(datetime(2015, 3, 3, 23, 59, 55)),
            "202.112.50.77",
            "GET",
            "/revue/JCHA/1995/v6/n1/031091ar.pdf",
            "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)",
            "202.112.50.77",
            "-",
            200,
        )

        self.assertFalse(is_pdf_download(record))

    def test_to_csv_row(self):
        record = Record(
            raw_timestamp="2015-03-03 23:59:55",
            proxy_ip="202.112.50.77",
            http_method="GET",
            url="/revue/ac/1995/v6/n1/031091ar.pdf",
            raw_user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:35.0) Gecko/20100101 Firefox/35.0",
            user_ip="202.112.50.77",
            raw_referer="http://www.bing.com/search?q=compare%20christ%20and%20bonhoeffer&pc=cosp&ptag=A0F73A159EF&form=CONBDF&conlogo=CT3210127",
            http_response_code="100"
        )

        self.assertEquals(to_csv_row(record).items(), [
            ("time", "2015-03-03 23:59:55"),
            ("date", "2015-03-03"),
            ("year", 2015),
            ("hour", 23),
            ("local_time", "2015-03-04 12:59:55"),
            ("local_date", "2015-03-04"),
            ("local_year", 2015),
            ("local_hour", 12),
            ("proxy_ip", '202.112.50.77'),
            ("user_ip", '202.112.50.77'),
            ("url", '/revue/ac/1995/v6/n1/031091ar.pdf'),
            ("referer", 'http://www.bing.com/search?q=compare%20christ%20and%20bonhoeffer&pc=cosp&ptag=A0F73A159EF&form=CONBDF&conlogo=CT3210127'),
            ("referer_host", 'www.bing.com'),
            ("continent", 'AS'),
            ("country", 'China'),
            ("geo_coordinates", "23.1167, 113.25"),
            ("timezone", 'Asia/Shanghai'),
            ("user_agent", 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:35.0) Gecko/20100101 Firefox/35.0'),
            ("browser", 'Firefox'),
            ("os", 'Mac OS X'),
            ("device", 'Other'),
            ("journal_name", 'ac'),
            # ("journal_domain", 'droit'),
            # ("full_oa", 'True'),
            ("publication_year", 1995),
            ("volume", 'v6'),
            ("issue", 'n1'),
            ("article_id", '031091'),
            ("age", 20),
            ("embargo", "False"),
        ])

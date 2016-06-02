# -*- coding: utf-8 -*-
from extract.extract import *
from extract.journals import *
from extract.activity_tracker import *
from datetime import datetime
from unittest import TestCase
from os import path

BASE_DIR = path.dirname(path.abspath(__file__))


class TestExtract(TestCase):

    def test_build_download_list(self):
        downloads, total, parsable = build_download_list([
            """2015-03-03 23:59:55 52.16.55.221 GET /revue/ac/1995/v6/n1/031091ar.pdf HTTP/1.1 - 80 - 52.16.55.221 "curl/7.35.0" "http://www.bing.com/search?q=compare%20christ%20and%20bonhoeffer&pc=cosp&ptag=A0F73A159EF&form=CONBDF&conlogo=CT3210127" 200 1306973""",
            """2015-03-03 23:59:55 - - 52.16.55.221 GET /revue/ac/1995/v6/n1/031091ar.pdf HTTP/1.1 - 80 - 52.16.55.221 "curl/7.35.0" "http://www.bing.com/search?q=compare%20christ%20and%20bonhoeffer&pc=cosp&ptag=A0F73A159EF&form=CONBDF&conlogo=CT3210127" 200 1306973""",
            """2015-03-03 23:59:55 52.16.55.221 GET /revue/ac/1995/v6/n1/031091ar.pdf HTTP/1.1 - 80 - 52.16.55.221 "curl/7.35.0" "http://www.bing.com/search?q=compare%20christ%20and%20bonhoeffer&pc=cosp&ptag=A0F73A159EF&form=CONBDF&conlogo=CT3210127" 404 1306973""",
        ], ActivityTracker(0))

        self.assertEquals(total, 3)
        self.assertEquals(parsable, 2)
        self.assertEquals(len(downloads), 1)

    def test_build_download_list_with_future_dates_are_parsable(self):
        downloads, total, parsable = build_download_list([
            """2015-03-03 23:59:55 52.16.55.221 GET /revue/ac/2033/v6/n1/031091ar.pdf HTTP/1.1 - 80 - 52.16.55.221 "curl/7.35.0" "http://www.bing.com/search?q=compare%20christ%20and%20bonhoeffer&pc=cosp&ptag=A0F73A159EF&form=CONBDF&conlogo=CT3210127" 200 1306973""",
        ], ActivityTracker(0))

        self.assertEquals(total, 1)
        self.assertEquals(parsable, 1)

    def test_line_extract_1(self):

        line = """2015-03-03 23:59:55 52.16.55.221 GET /revue/ac/1995/v6/n1/031091ar.pdf HTTP/1.1 - 80 - 52.16.55.221 "curl/7.35.0" "http://www.google.com/search?q=compare%20christ%20and%20bonhoeffer&pc=cosp&ptag=A0F73A159EF&form=CONBDF&conlogo=CT3210127" 200 1306973"""
        record = extract(line)
        self.assertIsNotNone(record)

        self.assertEqual(record.timestamp, get_montreal_time(datetime(2015, 3, 3, 23, 59, 55)))
        self.assertEqual(record.time, "2015-03-03 23:59:55")
        self.assertEqual(record.date, "2015-03-03")
        self.assertEqual(record.year, 2015)
        self.assertEqual(record.hour, 23)

        self.assertEqual(record.local_time, "2015-03-04 04:59:55")
        self.assertEqual(record.local_date, "2015-03-04")
        self.assertEqual(record.local_year, 2015)
        self.assertEqual(record.local_hour, 4)

        self.assertEqual(record.referer, "http://www.google.com/search?q=compare%20christ%20and%20bonhoeffer&pc=cosp&ptag=A0F73A159EF&form=CONBDF&conlogo=CT3210127")
        self.assertEqual(record.referer_host, "google")

        self.assertEqual(record.user_ip, "52.16.55.221")
        self.assertEqual(record.continent, "EU")
        self.assertEqual(record.country, "IE")
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
        self.assertEqual(record.device_type, "")
        self.assertFalse(record.is_good_robot)

        self.assertEqual(record.http_response_code, 200)

        self.assertEqual(record.age, 20)


    def test_line_extract_2(self):
        line = """2015-03-04 02:17:29 100.43.91.4 GET /revue/JCHA/2014/v6/n1/031091ar.pdf HTTP/1.1 - 80 - 100.43.91.4 "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)" "-" 200 6387"""
        record = extract(line)
        self.assertIsNotNone(record)

        self.assertEqual(record.timestamp, get_montreal_time(datetime(2015, 3, 4, 2, 17, 29)))
        self.assertEqual(record.proxy_ip, "100.43.91.4")
        self.assertEqual(record.http_method, "GET")
        self.assertEqual(record.url, "/revue/JCHA/2014/v6/n1/031091ar.pdf")

        self.assertEqual(record.user_ip, "100.43.91.4")
        self.assertEqual(record.country, "US")
        self.assertEqual(record.continent, "NA")
        self.assertEqual(record.timezone, "America/Los_Angeles")
        self.assertEqual(record.geo_coordinates, "37.4135, -122.1312")

        self.assertEqual(record.journal_name, "jcha")
        # self.assertEqual(record.journal_domain, "")

        self.assertEqual(record.raw_user_agent, "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)")
        self.assertEqual(record.browser, "YandexBot")
        self.assertEqual(record.os, "Other")
        self.assertEqual(record.device_type, "")
        self.assertTrue(record.is_good_robot)

        self.assertEqual(record.referer, "")
        self.assertEqual(record.http_response_code, 200)

        self.assertEqual(record.age, 1)


    def test_line_extract_3(self):
        line = """2015-03-04 00:29:36 222.33.68.117 GET /revue/JCHA/2015/v6/n1/031091ar.pdf HTTP/1.1 - 80 - 222.33.68.117 "-" "-" 400 460"""
        record = extract(line)
        self.assertIsNotNone(record)

        self.assertEqual(record.timestamp, get_montreal_time(datetime(2015, 3, 4, 0, 29, 36)))
        self.assertEqual(record.proxy_ip, "222.33.68.117")
        self.assertEqual(record.http_method, "GET")

        self.assertEqual(record.user_ip, "222.33.68.117")
        self.assertEqual(record.country, "CN")
        self.assertEqual(record.continent, "AS")
        self.assertEqual(record.timezone, "Asia/Shanghai")
        self.assertEqual(record.geo_coordinates, "39.9289, 116.3883")

        self.assertEqual(record.url, "/revue/JCHA/2015/v6/n1/031091ar.pdf")

        self.assertEqual(record.raw_user_agent, "-")
        self.assertEqual(record.browser, "Other")
        self.assertEqual(record.os, "Other")
        self.assertEqual(record.device_type, "")
        self.assertFalse(record.is_good_robot)

        self.assertEqual(record.referer, "")
        self.assertEqual(record.http_response_code, 400)

        self.assertEqual(record.age, 0)


    def test_line_extract_4(self):
        line = """2015-03-04 03:13:51 125.122.116.68 POST /revue/JCHA/1995/v6/n1/031091ar.pdf HTTP/1.1 - 80 - 125.122.116.68 "" "-" 200 6387"""
        record = extract(line)
        self.assertIsNotNone(record)

        self.assertEqual(record.timestamp, get_montreal_time(datetime(2015, 3, 4, 3, 13, 51)))
        self.assertEqual(record.proxy_ip, "125.122.116.68")
        self.assertEqual(record.http_method, "POST")

        self.assertEqual(record.user_ip, "125.122.116.68")
        self.assertEqual(record.country, "CN")
        self.assertEqual(record.continent, "AS")
        self.assertEqual(record.timezone, "Asia/Shanghai")
        self.assertEqual(record.geo_coordinates, "30.2936, 120.1614")

        self.assertEqual(record.url, "/revue/JCHA/1995/v6/n1/031091ar.pdf")

        self.assertEqual(record.raw_user_agent, "")
        self.assertEqual(record.browser, "")
        self.assertEqual(record.os, "")
        self.assertEqual(record.device_type, "")
        self.assertFalse(record.is_good_robot)

        self.assertEqual(record.referer, "")
        self.assertEqual(record.http_response_code, 200)

    def test_line_extract_5(self):
        """Space is accepted at the end of an url"""
        line = """2015-03-04 05:45:05 113.225.67.107 POST /F/AAH5hZjAp4REK7En3PgjyTX_  HTTP/1.1 - 80 - 113.225.67.107 "-" "-" 404 1385"""
        record = extract(line)
        self.assertIsNotNone(record)

    def test_line_extract_6(self):
        """Space in url are not accepted"""
        line = """2015-03-04 00:31:30 209.240.101.210 GET /bitstream/003422dd/1/Bulletin_CIRPEE_Winter 2011.pdf HTTP/1.1 - 80 - 209.240.101.210 "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:35.0) Gecko/20100101 Firefox/35.0" "https://depot.erudit.org/" 404 7340"""
        record = extract(line)
        self.assertIsNone(record)

    def test_line_extract_7(self):
        """Not a http protocol"""
        line = """2015-03-04 04:12:09 202.112.50.77 quit - 80 - 202.112.50.77 "-" "-" 200 6387"""
        record = extract(line)
        self.assertIsNone(record)

    def test_line_extract_8(self):
        """URL is not a download but is extracted anyway"""
        line = """2015-03-03 23:59:55 52.16.55.221 GET /favico HTTP/1.1 - 80 - 52.16.55.221 "curl/7.35.0" "-" 200 1306973"""
        record = extract(line)
        self.assertIsNotNone(record)

    def test_line_extract_9(self):
        """Missing http protocol is extracted anyway"""
        line = """2015-03-03 23:59:55 52.16.55.221 GET /favico - 80 - 52.16.55.221 "curl/7.35.0" "-" 200 1306973"""
        record = extract(line)
        self.assertIsNotNone(record)

    def test_line_extract_10(self):
        """Urls starting with http should be parsed"""
        line = """2014-03-05 03:26:07 5.57.6.26 GET http://www.erudit.org/images/hautOngletsRevue.png HTTP/1.1 - 80 - 5.57.6.26 "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:27.0) Gecko/20100101 Firefox/27.0" "http://www.erudit.org/css/general.css" 206 128"""
        record = extract(line)
        self.assertIsNotNone(record)

    def test_get_lines(self):
        lines = get_lines(path.join(BASE_DIR, "test-log.log"))
        self.assertEquals(len(list(lines)), 4)

    # def test_non_interesting_lines_are_discarded(self):
    #     line = """2015-03-04 04:12:09 202.112.50.77 quit - 80 - 202.112.50.77 "-" "-" 200 6387"""
    #     self.assertFalse(interesting_line(line))
    #
    # def test_interesting_lines_are_kept(self):
    #     line = """2015-03-03 23:59:55 52.16.55.221 GET  /revue/JCHA/1995/v6/n1/031091ar.pdf HTTP/1.1 - 80 - 52.16.55.221 "curl/7.35.0" "-" 200 1306973"""
    #     self.assertTrue(interesting_line(line))
    #
    # def test_html_lines_are_kept(self):
    #     line = """2015-03-03 23:59:55 52.16.55.221 GET  /revue/JCHA/1995/v6/n1/031091ar.html HTTP/1.1 - 80 - 52.16.55.221 "curl/7.35.0" "-" 200 1306973"""
    #     self.assertTrue(interesting_line(line))

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

        self.assertTrue(record.is_article_download)

    def test_record_is_not_download(self):
        record = Record(
            get_montreal_time(datetime(2015, 3, 3, 23, 59, 55)),
            "202.112.50.77",
            "GET",
            "/bitstream/003422dd/1/Bulletin_CIRPEE_Winter_2011.pdf",
            "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)",
            "202.112.50.77",
            "-",
            200,
        )

        self.assertFalse(record.is_article_download)

    def test_simple_extract_article_id(self):
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

        self.assertTrue(record.is_article_download)
        self.assertEquals(record.article_id, "400333")

    def test_simple_http_extract_article_id(self):
        record = Record(
            get_montreal_time(datetime(2015, 3, 3, 23, 59, 55)),
            "202.112.50.77",
            "GET",
            "https://www.erudit.org/revue/ltp/1987/v43/n3/400333ar.pdf",
            "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)",
            "202.112.50.77",
            "-",
            200,
        )

        self.assertTrue(record.is_article_download)
        self.assertEquals(record.article_id, "400333")

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

        self.assertEquals(record.to_csv_row(journals), [
            "2015-03-03 23:59:55",
            "2015-03-04 12:59:55",
            '202.112.50.77',
            '202.112.50.77',
            '/revue/ac/1995/v6/n1/031091ar.pdf',
            'bing',
            'AS',
            'CN',
            "23.1167, 113.25",
            'Asia/Shanghai',
            'Firefox',
            'Mac OS X',
            'p',
            'crimino',
            'v6',
            'n1',
            1995,
            '031091',
            20,
        ])

# -*- coding: utf-8 -*-
from extract.extract import *
from extract.activity_tracker import *
from datetime import datetime
from unittest import TestCase
from os import path
from extract.journals import JournalReferential

BASE_DIR = path.dirname(path.abspath(__file__))


class TestExtract(TestCase):

    journals = JournalReferential([
        {
            "id": "ltp",
            "other_ids": [],
            "names": [
                {"url_name": "ltp", "full_name": "ltp", "start_year": 1968, "stop_year": 1974},
            ],
            "full_text_html": [
              {"start_year": 1998, "stop_year": 2005},
              {"start_year": 2009}
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
            JournalReferential([]),
        )

        self.assertFalse(record.is_css_download)
        self.assertFalse(record.is_javascript_download)
        self.assertFalse(record.is_image_download)
        self.assertTrue(record.is_article_download)

    def test_html_is_not_considered_as_article_download_when_journals_says_so(self):


        record = Record(
            get_montreal_time(datetime(2015, 3, 3, 23, 59, 55)),
            "202.112.50.77",
            "GET",
            "/revue/ltp/1987/v43/n3/400333ar.html",
            "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)",
            "202.112.50.77",
            "-",
            200,
            self.journals,
        )

        self.assertFalse(record.is_css_download)
        self.assertFalse(record.is_javascript_download)
        self.assertFalse(record.is_image_download)
        self.assertFalse(record.is_article_download)

    def test_html_is_considered_as_article_download_when_journals_says_so(self):
        record = Record(
            get_montreal_time(datetime(2015, 3, 3, 23, 59, 55)),
            "202.112.50.77",
            "GET",
            "/revue/ltp/2000/v43/n3/400333ar.html",
            "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)",
            "202.112.50.77",
            "-",
            200,
            self.journals,
        )

        self.assertFalse(record.is_css_download)
        self.assertFalse(record.is_javascript_download)
        self.assertFalse(record.is_image_download)
        self.assertTrue(record.is_article_download)

    def test_html_with_random_parameters_is_not_considered_as_article_download(self):
        record = Record(
            get_montreal_time(datetime(2015, 3, 3, 23, 59, 55)),
            "202.112.50.77",
            "GET",
            "/revue/ltp/1987/v43/n3/400333ar.html?vue=biblio",
            "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)",
            "202.112.50.77",
            "-",
            200,
            JournalReferential([]),
        )

        self.assertFalse(record.is_css_download)
        self.assertFalse(record.is_javascript_download)
        self.assertFalse(record.is_image_download)
        self.assertFalse(record.is_article_download)

    def test_html_with_integral_view_is_considered_as_article_download(self):
        record = Record(
            get_montreal_time(datetime(2015, 3, 3, 23, 59, 55)),
            "202.112.50.77",
            "GET",
            "/revue/ltp/1987/v43/n3/400333ar.html?vue=integral",
            "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)",
            "202.112.50.77",
            "-",
            200,
            JournalReferential([]),
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
            JournalReferential([])
        )

        self.assertFalse(record.is_css_download)
        self.assertFalse(record.is_javascript_download)
        self.assertTrue(record.is_image_download)
        self.assertFalse(record.is_article_download)

    def test_geo_location_must_be_set_when_possible(self):
        record = Record(
            get_montreal_time(datetime(2015, 3, 3, 23, 59, 55)),
            "202.112.50.77",
            "GET",
            "toto.png",
            "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)",
            "202.112.50.77",
            "-",
            200,
            JournalReferential([])
        )

        self.assertEquals(record.country, "CN")
        self.assertEquals(record.region, "Guangdong")
        self.assertEquals(record.city, "Guangzhou")

    def test_state_must_be_null_when_it_makes_no_sense(self):
        record = Record(
            get_montreal_time(datetime(2015, 3, 3, 23, 59, 55)),
            "88.172.148.86",
            "GET",
            "toto.png",
            "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)",
            "88.172.148.86",
            "-",
            200,
            JournalReferential([])
        )

        self.assertEquals(record.country, "FR")
        self.assertEquals(record.region, u"Île-de-France")
        self.assertEquals(record.city, "Paris")

    def test_geo_location_should_be_empty_when_user_ip_is_not_readable(self):
        record = Record(
            get_montreal_time(datetime(2015, 3, 3, 23, 59, 55)),
            "202.112.50.77",
            "GET",
            "toto.png",
            "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)",
            "-",
            "-",
            200,
            JournalReferential([])
        )

        self.assertEquals(record.country, "")

    def test_clean_referer_host_mail(self):
        self.assertEquals(clean_referer_host("http://mail.google.com"), "email")
        self.assertEquals(clean_referer_host("http://mail.yahoo.com"), "email")

    def test_clean_referer_host_search_engine(self):
        self.assertEquals(clean_referer_host("http://www.google.com"), "google")
        self.assertEquals(clean_referer_host("http://www.google.it"), "google")
        self.assertEquals(clean_referer_host("http://www.google.tn"), "google")
        self.assertEquals(clean_referer_host("http://www.google.co.uk"), "google")
        self.assertEquals(clean_referer_host("http://www.google.co.ma"), "google")
        self.assertEquals(clean_referer_host("http://www.bing.com"), "bing")

    def test_clean_referer_host_scholar(self):
        self.assertEquals(clean_referer_host("http://scholar.google.com"), "scholar")

    def test_clean_referer_host_google_images(self):
        self.assertEquals(clean_referer_host("http://images.google.fr"), "google images")

    def test_clean_referer_host_google_translate(self):
        self.assertEquals(clean_referer_host("http://translate.google.com.vn/translate_p?hl=vi&langpair=en%7Cvi&u"), "google translate")

    def test_clean_referer_host_erudit(self):
        self.assertEquals(clean_referer_host("http://www.erudit.org/livre/aidelf/1988/000855co.pdf"), "erudit")

    def test_clean_referer_host_repere(self):
        self.assertEquals(clean_referer_host("http://repere.sdm.qc.ca/ipac20/ipac.jsp?session=13A11O56428H5.104373&profile=main--2frc&sourc"), "repere")
        self.assertEquals(clean_referer_host("http://repere2.sdm.qc.ca/ipac20/ipac.jsp?session=13A11O56428H5.104373&profile=main--2frc&sourc"), "repere")

    def test_clean_referer_host_teluq(self):
        self.assertEquals(clean_referer_host("http://benhur.teluq.uquebec.ca/~carrefou/carrefour310113.html"), "teluq")

    def test_clean_referer_host_facebook(self):
        self.assertEquals(clean_referer_host("http://www.facebook.com/l.php?u=http%3A%2F%2Fwww.erudit.org%2Frevue%2Fsmq%2F1990%2Fv15%2Fn2%2F031566ar.pdf&h=8cc09"), "facebook.com")

    def test_clean_referer_host_wikipedia(self):
        self.assertEquals(clean_referer_host("http://en.wikipedia.org"), "wikipedia")

    def test_clean_referer_host_unknown(self):
        self.assertEquals(clean_referer_host("http://www.toto.org"), "toto.org")
        self.assertEquals(clean_referer_host("http://www.ncbi.nlm.nih.gov"), "ncbi.nlm.nih.gov")
        self.assertEquals(clean_referer_host("http://ncbi.nlm.nih.gov"), "ncbi.nlm.nih.gov")
        self.assertEquals(clean_referer_host("http://ncbi.www.nlm.nih.gov"), "ncbi.www.nlm.nih.gov")

    def test_clean_referer_host_empty_host(self):
        self.assertEquals(clean_referer_host("http://"), "")

    def test_clean_referer_host_unknown(self):
        self.assertEquals(clean_referer_host("http://www.toto.org"), "toto.org")
        self.assertEquals(clean_referer_host("http://www.ncbi.nlm.nih.gov"), "ncbi.nlm.nih.gov")
        self.assertEquals(clean_referer_host("http://ncbi.nlm.nih.gov"), "ncbi.nlm.nih.gov")
        self.assertEquals(clean_referer_host("http://ncbi.www.nlm.nih.gov"), "ncbi.www.nlm.nih.gov")

    def test_pc_user_agent(self):
        user_agent = compute_user_agent("Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko")
        self.assertEquals(compute_device_type(user_agent), DEVICE_PC)

    def test_tablet_user_agent(self):
        user_agent = compute_user_agent("Mozilla/5.0 (Linux; U; Android 4.0.4; en-us; A211 Build/IMM76D) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Safari/534.30")
        self.assertEquals(compute_device_type(user_agent), DEVICE_TABLET)

    def test_mobile_user_agent(self):
        user_agent = compute_user_agent("Mozilla/5.0 (Linux; <Android Version>; <Build Tag etc.>) AppleWebKit/<WebKit Rev> (KHTML, like Gecko) Chrome/<Chrome Rev> Mobile Safari/<WebKit Rev>")
        self.assertEquals(compute_device_type(user_agent), DEVICE_MOBILE)

    def test_unknown_user_agent(self):
        user_agent = compute_user_agent("Mozilla/5.0")
        self.assertEquals(compute_device_type(user_agent), "")

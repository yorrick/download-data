# -*- coding: utf-8 -*-
from extract.common import *
from unittest import TestCase
from extract.activity_tracker import *
from extract.models import *


class TestCommon(TestCase):

    def test_good_robot_are_detected(self):
        activity_tracker = ActivityTracker()

        activity_tracker.register_activity(Record(
            get_montreal_time(datetime(2015, 3, 3, 23, 59, 55)),
            "202.112.50.77",
            "GET",
            "/revue/JCHA/1995/v6/n1/031091ar.pdf",
            "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)",
            "202.112.50.77",
            "-",
            200,
        ))

        self.assertEquals(activity_tracker.get_bots_user_ips(), {"202.112.50.77"})

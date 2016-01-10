# -*- coding: utf-8 -*-
from unittest import TestCase
from extract.activity_tracker import *
from extract.models import *


class TestCommon(TestCase):

    # if a session contains a request for robots.txt OR
    # OR its user-agent field is in the robot user-agent list
    # OR the HEAD method is used
    # OR (the referring field is always unassigned AND no images are requested) then classify the session as a Web robot
    # (Geens et al. en 2006)

    def human_record(self):
        """Builds a human record"""
        return Record(
            get_montreal_time(datetime(2015, 3, 3, 23, 59, 55)),
            "202.112.50.77",
            "GET",
            "/revue/JCHA/1995/v6/n1/031091ar.pdf",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:35.0) Gecko/20100101 Firefox/35.0",
            "202.112.50.77",
            "some-referer",
            200)

    def test_regular_activity_is_not_considered_as_robot(self):
        activity_tracker = ActivityTracker(0)
        activity_tracker.register_activity(self.human_record())

        self.assertEquals(activity_tracker.get_bots_user_ips, set())

    def test_robots_declared_in_user_agent_are_detected(self):
        activity_tracker = ActivityTracker(0)

        robot_activity = self.human_record()
        robot_activity.raw_user_agent = "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)"
        activity_tracker.register_activity(self.human_record(), robot_activity)

        self.assertEquals(activity_tracker.get_bots_user_ips, {"202.112.50.77"})

    def test_requests_fetching_robots_txt_are_detected(self):
        activity_tracker = ActivityTracker(0)

        robot_activity = self.human_record()
        robot_activity.url = "/robots.txt"
        activity_tracker.register_activity(self.human_record(), robot_activity)


        self.assertEquals(activity_tracker.get_bots_user_ips, {"202.112.50.77"})

    def test_using_heads_is_detected(self):
        activity_tracker = ActivityTracker(0)

        robot_activity = self.human_record()
        robot_activity.http_method = "HEAD"
        activity_tracker.register_activity(self.human_record(), robot_activity)

        self.assertEquals(activity_tracker.get_bots_user_ips, {"202.112.50.77"})

    def test_no_referer_no_image(self):
        activity_tracker = ActivityTracker(0)

        robot_activity = self.human_record()
        robot_activity.raw_referer = "-"
        activity_tracker.register_activity(robot_activity)

        self.assertEquals(activity_tracker.get_bots_user_ips, {"202.112.50.77"})

    def test_no_referer_no_image_but_below_threshold_is_not_detected(self):
        activity_tracker = ActivityTracker(2)

        robot_activity = self.human_record()
        robot_activity.raw_referer = "-"
        activity_tracker.register_activity(robot_activity)

        self.assertEquals(activity_tracker.get_bots_user_ips, set())

    def test_setting_referer_once_is_considered_human(self):
        activity_tracker = ActivityTracker(0)

        robot_activity = self.human_record()
        robot_activity.raw_referer = "-"
        activity_tracker.register_activity(self.human_record(), robot_activity)

        self.assertEquals(activity_tracker.get_bots_user_ips, set())

    def test_fetching_one_image_is_considered_human(self):
        activity_tracker = ActivityTracker(0)

        image_activity = self.human_record()
        image_activity.url = "toto.png"

        robot_activity = self.human_record()
        robot_activity.raw_referer = "-"
        activity_tracker.register_activity(image_activity, robot_activity)

        self.assertEquals(activity_tracker.get_bots_user_ips, set())

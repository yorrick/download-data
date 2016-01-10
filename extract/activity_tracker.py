#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import defaultdict
from collections import OrderedDict
from common import *


class ActivityTracker():

    def __init__(self):
        self.total = defaultdict(lambda: 0)

        self.good_robot = defaultdict(lambda: 0)
        self.fetch_robots_txt = defaultdict(lambda: 0)
        self.head_used = defaultdict(lambda: 0)
        self.referer_set = defaultdict(lambda: 0)
        self.image_fetched = defaultdict(lambda: 0)

    def register_activity(self, *records):
        for record in records:
            self._register_activity(record)

    def _register_activity(self, record):
        self.total[record.user_ip] += 1

        if record.is_good_robot:
            self.good_robot[record.user_ip] += 1

        if record.url == "/robots.txt":
            self.fetch_robots_txt[record.user_ip] += 1

        if record.http_method == "HEAD":
            self.head_used[record.user_ip] += 1

        if record.referer:
            self.referer_set[record.user_ip] += 1

        if record.is_image_download:
            self.image_fetched[record.user_ip] += 1

    @cached_property
    def get_bots_user_ips(self):
        no_referer = set(self.total.keys()).difference(self.referer_set.keys())
        no_images = set(self.total.keys()).difference(self.image_fetched.keys())

        no_referer_no_image = no_referer.intersection(no_images)

        return set(
            self.good_robot.keys() +
            self.fetch_robots_txt.keys() +
            self.head_used.keys()
        ).union(no_referer_no_image)

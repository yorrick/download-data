#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import defaultdict
from collections import OrderedDict
from common import *


class ActivityTracker():

    def __init__(self):
        self.total = defaultdict(lambda: 0)
        self.download = defaultdict(lambda: 0)
        self.good_robot = defaultdict(lambda: 0)
        self.other = defaultdict(lambda: 0)
        self.css = defaultdict(lambda: 0)
        self.javascript = defaultdict(lambda: 0)
        self.image = defaultdict(lambda: 0)

    def register_activity(self, *records):
        for record in records:
            self._register_activity(record)

    def _register_activity(self, record):
        self.total[record.user_ip] += 1

        if record.is_article_download:
            self.download[record.user_ip] += 1

        if record.is_css_download:
            self.css[record.user_ip] += 1

        if record.is_javascript_download:
            self.javascript[record.user_ip] += 1

        if record.is_image_download:
            self.image[record.user_ip] += 1

        if record.is_good_robot:
            self.good_robot[record.user_ip] += 1
        else:
            self.other[record.user_ip] += 1

    @cached_property
    def get_bots_user_ips(self):
        return set(self.good_robot.keys())

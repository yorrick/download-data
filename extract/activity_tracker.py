#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import defaultdict
from collections import OrderedDict


class Activity():

    def __init__(self, user_ip, total, download, good_robot, maybe_human,
                 css, javascript, image):
        self.user_ip = user_ip
        self.total = total
        self.download = download
        self.good_robot = good_robot
        self.maybe_human = maybe_human
        self.css = css
        self.javascript = javascript
        self.image = image
        self.download_ratio = self.download * 100.0 / self.total

    def __str__(self):
        return "Activity({:15}, total: {:5}, download: {:5} (download_ratio: {:4.2f}%), good_robot: {:5}, other: {:5})".format(
            self.user_ip, self.total, self.download,
            self.download_ratio, self.good_robot, self.other)

    def __repr__(self):
        return str(self)

    def to_csv_row(self):
        return OrderedDict(
            [
                ('user_ip', self.user_ip),
                ('total', self.total),
                ('download', self.download),
                ('good_robot', self.good_robot),
                ('maybe_human', self.maybe_human),
                ('download', self.download),
                ('css', self.css),
                ('javascript', self.javascript),
                ('image', self.image),
            ]
        )


class ActivityTracker():

    def __init__(self):
        self.total = defaultdict(lambda: 0)
        self.download = defaultdict(lambda: 0)
        self.good_robot = defaultdict(lambda: 0)
        self.other = defaultdict(lambda: 0)
        self.css = defaultdict(lambda: 0)
        self.javascript = defaultdict(lambda: 0)
        self.image = defaultdict(lambda: 0)

    def register_activity(self, record):
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

    def get_bots_user_ips(self):
        return {}

#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import defaultdict
from common import *


class ActivityTracker():

    def __init__(self, total_number_threshold):
        self.total_number_threshold = total_number_threshold

        self.total = defaultdict(lambda: 0)
        self.downloads = defaultdict(lambda: 0)

        self.good_robot = defaultdict(lambda: 0)
        self.fetch_robots_txt = defaultdict(lambda: 0)
        self.head_used = defaultdict(lambda: 0)
        self.referer_set = defaultdict(lambda: 0)
        self.image_fetched = defaultdict(lambda: 0)
        self.javascript_fetched = defaultdict(lambda: 0)
        self.css_fetched = defaultdict(lambda: 0)

    def register_activity(self, *records):
        for record in records:
            self._register_activity(record)

    def _register_activity(self, record):
        self.total[record.user_ip] += 1

        if record.is_article_download:
            self.downloads[record.user_ip] += 1

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

        if record.is_javascript_download:
            self.javascript_fetched[record.user_ip] += 1

        if record.is_css_download:
            self.css_fetched[record.user_ip] += 1

    @cached_property
    def good_bots_user_ips(self):
        return set(self.good_robot.keys())

    @cached_property
    def lots_of_downloads_user_ips(self):
        return {user_ip for user_ip, count in self.total.items()
                             if count > self.total_number_threshold}

    @cached_property
    def no_referer_no_images_user_ips(self):
        no_referer = set(self.total.keys()).difference(self.referer_set.keys())
        no_images = set(self.total.keys()).difference(self.image_fetched.keys())
        return no_referer.intersection(no_images)

    @cached_property
    def no_images_no_javascript_no_css_user_ips(self):
        no_images = set(self.total.keys()).difference(self.image_fetched.keys())
        no_javascript = set(self.total.keys()).difference(self.javascript_fetched.keys())
        no_css = set(self.total.keys()).difference(self.css_fetched.keys())

        return no_images.intersection(no_javascript).intersection(no_css)

    @cached_property
    def bad_bots_user_ips(self):
        lots_of_downloads = self.lots_of_downloads_user_ips
        no_referer_no_images = self.no_referer_no_images_user_ips
        no_images_no_javascript_no_css = self.no_images_no_javascript_no_css_user_ips

        bad_bots_user_ips = set(
            self.fetch_robots_txt.keys() +
            self.head_used.keys()
        )\
            .union(no_referer_no_images.intersection(lots_of_downloads))\
            .union(no_images_no_javascript_no_css.intersection(lots_of_downloads))

        return bad_bots_user_ips.difference(self.good_bots_user_ips)

    @cached_property
    def bots_user_ips(self):
        return self.good_bots_user_ips.union(self.bad_bots_user_ips)

    def get_info_for_user_ip(self, user_ip):
        return """
        Detail for user ip {}
        Total: {}
        Download: {}
        Good robot: {}
        Fetch robot.txt: {}
        Head used: {}
        Referer set: {}
        Image fetched: {}
        Javascript fetched: {}
        Css fetched: {}
        """.format(
            user_ip,
            self.total[user_ip],
            self.downloads[user_ip],
            self.good_robot[user_ip],
            self.fetch_robots_txt[user_ip],
            self.head_used[user_ip],
            self.referer_set[user_ip],
            self.image_fetched[user_ip],
            self.javascript_fetched[user_ip],
            self.css_fetched[user_ip],
        )

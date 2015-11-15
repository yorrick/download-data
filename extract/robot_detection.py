#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import defaultdict


class RobotDetectorResult():

    def __init__(self, user_ip, download_count, line_example, proxy_ips):
        self.user_ip = user_ip
        self.download_count = download_count
        self.line_example = line_example
        self.proxy_ips = proxy_ips


class RobotDetector():

    def __init__(self, download_number_threshold):
        self.download_number_threshold = download_number_threshold
        self.downloads_per_user_ip = defaultdict(lambda: 0)
        self.proxy_ips_per_user_ip = defaultdict(list)
        self.line_samples = dict()

    def register_csv_row(self, csv_row):
        if self.download_number_threshold is None:
            return

        user_ip = csv_row["user_ip"]
        proxy_ip = csv_row["proxy_ip"]

        self.downloads_per_user_ip[user_ip] += 1
        self.proxy_ips_per_user_ip[user_ip].append(proxy_ip)

        if user_ip not in self.line_samples:
            self.line_samples[user_ip] = csv_row

    def get_suspicious_ips(self):
        if self.download_number_threshold is None:
            return []

        results = [RobotDetectorResult(
            user_ip,
            download_count,
            self.line_samples[user_ip],
            set(self.proxy_ips_per_user_ip[user_ip])
        ) for user_ip, download_count in self.downloads_per_user_ip.items()
                          if download_count >= self.download_number_threshold]

        return sorted(results, key=lambda result: -result.download_count)

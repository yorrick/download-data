#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import defaultdict


class RobotDetector():

    download_number_threshold = 300

    def __init__(self, detect = True):
        self.detect = detect
        self.downloads_per_user_ip = defaultdict(lambda: 0)
        self.line_samples = dict()

    def register_csv_row(self, csv_row):
        if not self.detect:
            return

        ip = csv_row["user_ip"]
        self.downloads_per_user_ip[ip] += 1

        if ip not in self.line_samples:
            self.line_samples[ip] = csv_row

    def get_suspicious_ips(self):
        if not self.detect:
            return []

        suspicious_ips = [(ip, count, self.line_samples[ip]) for ip, count in self.downloads_per_user_ip.items()
                          if count >= self.download_number_threshold]
        return sorted(suspicious_ips, key=lambda tup: -tup[1])

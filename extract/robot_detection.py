#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import defaultdict


class RobotDetector():
    downloads_per_user_ip = defaultdict(lambda: 0)
    line_samples = dict()

    @classmethod
    def register_csv_row(cls, csv_row):
        ip = csv_row["user_ip"]
        cls.downloads_per_user_ip[ip] += 1

        if ip not in cls.line_samples:
            cls.line_samples[ip] = csv_row

    @classmethod
    def get_suspicious_ips(cls, download_number_threshold):
        suspicious_ips = [(ip, count, cls.line_samples[ip]) for ip, count in cls.downloads_per_user_ip.items()
                          if count >= download_number_threshold]
        return sorted(suspicious_ips, key=lambda tup: -tup[1])

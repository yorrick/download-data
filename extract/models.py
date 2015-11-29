# -*- coding: utf-8 -*-
from common import cached_property
from datetime_utils import *
from urlparse import urlparse


class Record():

    def __init__(self, timestamp, proxy_ip, http_method, url, journal,
                 user_agent, raw_user_agent, user_ip, geo_location, raw_referer, http_response_code):
        self.timestamp = timestamp

        self.proxy_ip = proxy_ip
        self.http_method = http_method
        self.url = url
        self.journal = journal
        self.user_agent = user_agent
        self.raw_user_agent = raw_user_agent
        self.user_ip = user_ip
        self.geo_location = geo_location
        self.raw_referer = raw_referer
        self.http_response_code = http_response_code

    @cached_property
    def time(self):
        return self.timestamp.strftime(TIMESTAMP_FORMAT)

    @cached_property
    def date(self):
        return self.timestamp.strftime(DATE_FORMAT)

    @cached_property
    def year(self):
        return self.timestamp.year

    @cached_property
    def hour(self):
        return self.timestamp.hour

    @cached_property
    def local_timestamp(self):
        local_tz = self.geo_location.timezone if self.geo_location is not None else None
        return to_local_time(self.timestamp, local_tz)

    @cached_property
    def local_time(self):
        return self.local_timestamp.strftime(TIMESTAMP_FORMAT)

    @cached_property
    def local_date(self):
        return self.local_timestamp.strftime(DATE_FORMAT)

    @cached_property
    def local_year(self):
        return self.local_timestamp.year

    @cached_property
    def local_hour(self):
        return self.local_timestamp.hour

    @cached_property
    def referer(self):
        return '' if self.raw_referer == '-' else self.raw_referer

    @cached_property
    def referer_host(self):
        if not self.referer:
            return ''
        else:
            # return '' if url could not be parsed
            return urlparse(self.referer).netloc


class Journal():

    def __init__(self, name, year, volume, issue, article_id):
        self.name = name
        self.year = year
        self.volume = volume
        self.issue = issue
        self.article_id = article_id

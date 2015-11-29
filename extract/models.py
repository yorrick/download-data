# -*- coding: utf-8 -*-
from common import *
from datetime_utils import *
from urlparse import urlparse
from geoip import geolite2
from datetime import datetime
from countries import COUNTRIES


class Record():

    def __init__(self, raw_timestamp, proxy_ip, http_method, url, journal,
                 user_agent, raw_user_agent, user_ip, raw_referer, http_response_code):
        self.raw_timestamp = raw_timestamp  ## string version of timestamp
        self.proxy_ip = proxy_ip
        self.http_method = http_method
        self.url = url
        self.journal = journal
        self.user_agent = user_agent
        self.raw_user_agent = raw_user_agent
        self.user_ip = user_ip
        self.raw_referer = raw_referer  # raw version of user agent
        self.http_response_code = http_response_code

    @cached_property
    def timestamp(self):
        return get_montreal_time(datetime.strptime(self.raw_timestamp, TIMESTAMP_FORMAT))

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
        return to_local_time(self.timestamp, self.timezone) if self.timezone else ''

    @cached_property
    def local_time(self):
        return self.local_timestamp.strftime(TIMESTAMP_FORMAT) if self.local_timestamp else ''

    @cached_property
    def local_date(self):
        return self.local_timestamp.strftime(DATE_FORMAT) if self.local_timestamp else ''

    @cached_property
    def local_year(self):
        return self.local_timestamp.year if self.local_timestamp else ''

    @cached_property
    def local_hour(self):
        return self.local_timestamp.hour if self.local_timestamp else ''

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

    @cached_property
    def _geo_location(self):
        return compute_ip_geo_location(self.user_ip)

    @cached_property
    def continent(self):
        return self._geo_location.continent if self._geo_location else ''

    @cached_property
    def country(self):
        return COUNTRIES.get(self._geo_location.country, self._geo_location.country) if self._geo_location else ''


    @cached_property
    def geo_coordinates(self):
        if self._geo_location:
            location = self._geo_location.location
            return ", ".join([str(loc) for loc in location]) if location is not None else ""
        else:
            return ''

    @cached_property
    def timezone(self):
        if self._geo_location:
            timezone = self._geo_location.timezone
            return '' if timezone == 'None' else timezone
        else:
            return ''


class Journal():

    def __init__(self, name, year, volume, issue, article_id):
        self.name = name
        self.year = year
        self.volume = volume
        self.issue = issue
        self.article_id = article_id


@memoize_single_arg
def compute_ip_geo_location(raw_ip):
    return geolite2.lookup(raw_ip)

# -*- coding: utf-8 -*-
from common import *
from datetime_utils import *
from urlparse import urlparse
from geoip import geolite2
from datetime import datetime
from countries import COUNTRIES
from user_agents import parse
import re


# /revue/JCHA/1995/v6/n1/031091ar.pdf
JOURNAL_REGEX = re.compile("/revue/(?P<name>[^/]+)/(?P<year>\d{4})/(?P<volume>[^/]+)/(?P<issue>[^/]+)/(?P<article_id>[^/]+)ar(.pdf|.html)")


class Record():

    def __init__(self, raw_timestamp, proxy_ip, http_method, url,
                 raw_user_agent, user_ip, raw_referer, http_response_code):
        self.raw_timestamp = raw_timestamp  ## string version of timestamp
        self.proxy_ip = proxy_ip
        self.http_method = http_method
        self.url = url
        self.raw_user_agent = raw_user_agent
        self.user_ip = user_ip
        self.referer = '' if raw_referer == '-' else raw_referer
        self.http_response_code = int(http_response_code)

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

    @cached_property
    def user_agent(self):
        return compute_user_agent(self.raw_user_agent) if self.raw_user_agent else ''

    @cached_property
    def browser(self):
        return self.user_agent.browser.family if self.user_agent else ''

    @cached_property
    def os(self):
        return self.user_agent.os.family if self.user_agent else ''

    @cached_property
    def device(self):
        return self.user_agent.device.family if self.user_agent else ''

    @cached_property
    def is_bot(self):
        return self.user_agent.is_bot if self.user_agent else ''

    @cached_property
    def is_bot(self):
        return self.user_agent.is_bot if self.user_agent else ''

    @cached_property
    def _journal_match(self):
        match = JOURNAL_REGEX.match(self.url)
        return match.groupdict() if match else {}

    @cached_property
    def journal_name(self):
        return self._journal_match["name"].lower() if self._journal_match else ''

    @cached_property
    def publication_year(self):
        return int(self._journal_match["year"]) if self._journal_match else ''

    @cached_property
    def volume(self):
        return self._journal_match["volume"] if self._journal_match else ''

    @cached_property
    def issue(self):
        return self._journal_match["issue"] if self._journal_match else ''

    @cached_property
    def article_id(self):
        return self._journal_match["article_id"] if self._journal_match else ''

    @cached_property
    def age(self):
        return self.year - self.publication_year if self.publication_year else ''

    @cached_property
    def embargo(self):
        return self.age <= 2


@memoize_single_arg
def compute_ip_geo_location(raw_ip):
    return geolite2.lookup(raw_ip)


@memoize_single_arg
def compute_user_agent(raw_user_agent):
    return parse(raw_user_agent)

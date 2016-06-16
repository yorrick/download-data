# -*- coding: utf-8 -*-
from common import *
from datetime_utils import *
from datetime import datetime
from geolocalization import GEO_DB
from user_agents import parse
import re
from referer_parser import Referer
from repoze.lru import lru_cache


# /revue/JCHA/1995/v6/n1/031091ar.pdf
JOURNAL_REGEX = re.compile("(https?://www.erudit.org)?/revue/(?P<name>[^/]+)/(?P<year>\d{4})/(?P<volume>[^/]+)/(?P<issue>[^/]+)/(?P<article_id>[^/?]+)ar(.pdf|.html|.html\?vue=integral)$")
IMAGE_EXTENSIONS = (
    '.png',
    '.jpeg',
    '.jpg',
)


# list of device types
DEVICE_MOBILE = "m"
DEVICE_TABLET = "t"
DEVICE_PC = "p"


def compute_device_type(user_agent):
    if user_agent.is_mobile:
        return DEVICE_MOBILE
    elif user_agent.is_tablet:
        return DEVICE_TABLET
    elif user_agent.is_pc:
        return DEVICE_PC
    else:
        return ''


class Record():

    def __init__(self, raw_timestamp, proxy_ip, http_method, url,
                 raw_user_agent, user_ip, raw_referer, http_response_code, journal_ref):
        self.raw_timestamp = raw_timestamp  ## string version of timestamp
        self.proxy_ip = proxy_ip
        self.http_method = http_method
        self.url = url
        self.raw_user_agent = raw_user_agent
        self.user_ip = user_ip
        self.raw_referer = raw_referer
        self.http_response_code = int(http_response_code)
        self.journal_ref = journal_ref

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
            return clean_referer_host(self.referer)

    @cached_property
    def _geo_location(self):
        return compute_ip_geo_location(self.user_ip)

    @cached_property
    def continent(self):
        return self._geo_location.continent if self._geo_location else ''

    @cached_property
    def country(self):
        return self._geo_location.country if self._geo_location else ''

    @cached_property
    def city(self):
        if self._geo_location and self._geo_location.get_info_dict().get('city'):
            return self._geo_location.get_info_dict().get('city').get('names').get('en') or ''
        else:
            return ''

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
    def device_type(self):
        return compute_device_type(self.user_agent) if self.user_agent else ''


    @cached_property
    def is_good_robot(self):
        return self.user_agent.is_bot if self.user_agent else ''

    @cached_property
    def is_css_download(self):
        return self.url.endswith(".css")

    @cached_property
    def is_javascript_download(self):
        return self.url.endswith(".js")

    @cached_property
    def is_image_download(self):
        return any(self.url.endswith(extension) for extension in IMAGE_EXTENSIONS)

    @cached_property
    def _journal_match(self):
        match = JOURNAL_REGEX.match(self.url)
        return match.groupdict() if match else {}

    @cached_property
    def is_article_download(self):
        if bool(self._journal_match) and self.http_response_code == 200 and self.http_method == "GET":
            if self.url.endswith(".html"):
                return self.journal_ref.is_html_a_download(self.journal_id, self.publication_year)
            else:
                return True
        else:
            return False

    @cached_property
    def journal_id(self):
        return self.journal_ref.get_journal_id(self.journal_name) if self.journal_name else ''

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

    def to_csv_row(self, is_robot, bad_robot, minimum_fields):
        return [
            self.time,
            self.local_time,
            self.proxy_ip[:20],
            self.user_ip[:32],
        ] + ([self.url[:500]] if not minimum_fields else []) + \
        [
            self.referer_host[:100],
            self.continent[:10] if self.continent else '',
            self.country[:2] if self.country else '',
            self.city[:50] if self.city else '',
        ] + ([self.geo_coordinates[:100] if self.geo_coordinates else ''] if not minimum_fields else []) + \
        [
            self.timezone[:100] if self.timezone else '',

            self.browser[:200],
            self.os[:200],
            self.device_type[:1],

            self.journal_id[:20],
            self.volume[:20],
            self.issue[:20],
            self.publication_year,
            self.article_id[:20],

            self.age,
        ] + ([is_robot, bad_robot] if not minimum_fields else [])


@lru_cache(20000)
def compute_ip_geo_location(raw_ip):
    # some ips look like 129.195.207.79, 129.195.0.205 and are not valid, others look like "-"
    try:
        return GEO_DB.lookup(raw_ip)
    except Exception as e:
        return None


@lru_cache(20000)
def compute_user_agent(raw_user_agent):
    return parse(raw_user_agent)


SEARCH_MEDIUM_REFERERS = {
    "scholar.google": "scholar",
    "translate.google.": "google translate",
}


UNKNOWN_MEDIUM_REFERERS = {
    "erudit.": "erudit",
    "repere.sdm.qc.ca": "repere",
    "repere2.sdm.qc.ca": "repere",
    "teluq.uquebec.ca": "teluq",
    "google.tn": "google",
    "wikipedia.org": "wikipedia",
}


def _strip_www(string):
    return re.sub(r"""^www.""", "", string)


def _replace_referer_with(r, replacement_dict):
    special_referers = [referer for string, referer in replacement_dict.items()
                            if string in r.uri.netloc]

    if special_referers:
        # take first
        return special_referers[0].lower()

    if r.referer is not None:
        return r.referer.lower()
    else:
        return _strip_www(r.uri.netloc)


def clean_referer_host(referer_host):
    try:
        r = Referer(referer_host)
    except Exception as e:
        return ''

    if r.medium == "email":
        return "email"
    elif r.medium == "search":
        return _replace_referer_with(r, SEARCH_MEDIUM_REFERERS)
    elif r.medium == "unknown":
        return _replace_referer_with(r, UNKNOWN_MEDIUM_REFERERS)
    else:
        return _strip_www(r.uri.netloc)


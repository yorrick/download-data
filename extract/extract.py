# -*- coding: utf-8 -*-
from __future__ import print_function
import re
from models import *
from datetime import datetime
import codecs
from user_agents import parse
from geoip import geolite2
from collections import OrderedDict
from countries import COUNTRIES
from datetime_utils import *


TIMESTAMP_REGEX = "\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
IP_REGEX = "\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
HTTP_METHOD_REGEX = "([^\s]+)"
PORT_REGEX = "\d{1,5}"
URL_REGEX = "/revue/[^\s]+ar(.pdf|.html)"
# URL_REGEX = "/revue/[^\s]+ar.pdf"
PROTOCOL_REGEX = "HTTP/1.[01] "
USER_AGENT_REGEX = "[^\"]*"
REFERER_REGEX = "[^\"]*"
HTTP_RETURN_CODE_REGEX = "[1-5]\d{2}"

# /revue/JCHA/1995/v6/n1/031091ar.pdf
JOURNAL_REGEX = re.compile("/revue/(?P<name>[^/]+)/(?P<year>\d{4})/(?P<volume>[^/]+)/(?P<issue>[^/]+)/(?P<article_id>[^/]+)ar(.pdf|.html)")

LOG_REGEX = re.compile("""^(?P<timestamp>{timestamp}) (?P<proxy_ip>{ip}) (?P<http_method>{http_method}) (?P<url>{url}) ({protocol})?- {port} - (?P<user_ip>{ip}) \"(?P<raw_user_agent>{user_agent})\" \"(?P<raw_referer>{raw_referer})\" (?P<http_response_code>{http_response_code}) .+$""".format(
    timestamp = TIMESTAMP_REGEX,
    ip = IP_REGEX,
    http_method = HTTP_METHOD_REGEX,
    port = PORT_REGEX,
    url = URL_REGEX,
    protocol = PROTOCOL_REGEX,
    user_agent = USER_AGENT_REGEX,
    http_response_code = HTTP_RETURN_CODE_REGEX,
    raw_referer = REFERER_REGEX,
))


LINE_FILTERS = [
    lambda line: "/revue/" in line and ("ar.html" in line or "ar.pdf" in line),
    lambda line: "GET" in line,
    lambda line: "200" in line,
]


def interesting_line(log_line):
    return all([filter(log_line) for filter in LINE_FILTERS])


def extract(log_line):
    match = LOG_REGEX.match(log_line)

    if match is not None:
        groups = match.groupdict()
        # parse timestamp
        # do not handle ambiguous timestamps, due to time changes of 1 hour between seasons
        groups["timestamp"] = get_log_time(datetime.strptime(groups["timestamp"], TIMESTAMP_FORMAT))
        groups["geo_location"] = compute_ip_geo_location(groups["user_ip"])
        groups["http_response_code"] = int(groups["http_response_code"])
        groups["user_agent"] = compute_user_agent(groups["raw_user_agent"])
        groups["journal"] = extract_journal(groups["url"])

        return Record(**groups)
    else:
        return None


def extract_journal(url):
    match = JOURNAL_REGEX.match(url)

    if match is None:
        return Journal(None, None, None, None, None)

    groups = match.groupdict()
    groups["name"] = groups["name"].lower()
    groups["year"] = int(groups["year"])

    return Journal(**groups)


def get_lines(source_file, encoding = "utf-8"):
    with codecs.open(source_file, "r", encoding=encoding) as f:
        for line in f:
            yield line


def is_pdf_download(record):
    return not record.user_agent.is_bot and record.http_response_code == 200 and record.http_method == "GET"


# http://code.activestate.com/recipes/578231-probably-the-fastest-memoization-decorator-in-the-/
def memoize_single_arg(f):
    class memodict(dict):
        __slots__ = ()
        def __missing__(self, key):
            self[key] = ret = f(key)
            return ret

    return memodict().__getitem__


@memoize_single_arg
def compute_user_agent(raw_user_agent):
    return parse(raw_user_agent)


@memoize_single_arg
def compute_ip_geo_location(raw_ip):
    return geolite2.lookup(raw_ip)


def get_geo_location_info(geo_location):
    if geo_location is not None:
        location_string = ", ".join([str(loc) for loc in geo_location.location]) if geo_location.location is not None else ""

        tz = '' if geo_location.timezone == 'None' else geo_location.timezone
        country = COUNTRIES.get(geo_location.country, geo_location.country)

        return [
            ("user_ip", geo_location.ip),
            ("continent", geo_location.continent),
            ("country", country),
            ("geo_coordinates", location_string),
            ("timezone", tz),
        ]
    else:
        return [
            ("user_ip", ""),
            ("continent", ""),
            ("country", ""),
            ("geo_coordinates", ""),
            ("timezone", ""),
        ]


def get_user_agent_info(user_agent):
    if user_agent is not None:
        return [
            ("browser", user_agent.browser.family),
            ("os", user_agent.os.family),
            ("device", user_agent.device.family),
        ]
    else:
        return [
            ("browser", ""),
            ("os", ""),
            ("device", ""),
        ]


def get_journal_info(journal):
    if journal is not None:
        return [
            ("journal_name", journal.name),
            ("publication_year", journal.year),
            ("volume", journal.volume),
            ("issue", journal.issue),
            ("article_id", journal.article_id),
        ]
    else:
        return [
            ("journal_name", ""),
            ("publication_year", ""),
            ("volume", ""),
            ("issue", ""),
            ("article_id", ""),
        ]


def compute_age(download_year, publication_year):
    if publication_year is None:
        return None

    return download_year - publication_year


def to_csv_row(record):
    return OrderedDict(
        [
            ('time', record.time),
            ('date', record.date),
            ('year', record.year),
            ('hour', record.hour),
            ('local_time', record.local_time),
            ('local_date', record.local_date),
            ('local_year', record.local_year),
            ('local_hour', record.local_hour),
            ('proxy_ip', record.proxy_ip),
            ('user_ip', record.user_ip),
            ('url', record.url),
            ('referer', record.referer),
            ('referer_host', record.referer_host),
        ] + \
        get_geo_location_info(record.geo_location) + \
        [("user_agent", record.raw_user_agent)] + \
        get_user_agent_info(record.user_agent) + \
        get_journal_info(record.journal) + \
        [("age", compute_age(record.timestamp.year, record.journal.year))]
    )

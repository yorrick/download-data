# -*- coding: utf-8 -*-
from __future__ import print_function
import re
from models import *
from datetime import datetime
import codecs
import sys
from user_agents import parse
from geoip import geolite2
from collections import namedtuple, OrderedDict


TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
TIMESTAMP_REGEX = "\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
IP_REGEX = "\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
HTTP_METHOD_REGEX = "([^\s]+)"
PORT_REGEX = "\d{1,5}"
URL_REGEX = "/revue/[^\s]+ar(.pdf|.html)"
PROTOCOL_REGEX = "HTTP/1.[01] "
USER_AGENT_REGEX = "[^\"]*"
REFERER_REGEX = "[^\"]*"
HTTP_RETURN_CODE_REGEX = "[1-5]\d{2}"

# /revue/JCHA/1995/v6/n1/031091ar.pdf
JOURNAL_REGEX = "/revue/(?P<name>[^/]+)/(?P<year>\d{4})/(?P<volume>[^/]+)/(?P<issue>[^/]+)/(?P<article_id>[^/]+)ar(.pdf|.html)"

LOG_REGEX = """^(?P<timestamp>{timestamp}) (?P<first_ip>{ip}) (?P<http_method>{http_method}) (?P<url>{url}) ({protocol})?- {port} - (?P<second_ip>{ip}) \"(?P<raw_user_agent>{user_agent})\" \"(?P<referer>{referer})\" (?P<http_response_code>{http_response_code}) .+$""".format(
    timestamp = TIMESTAMP_REGEX,
    ip = IP_REGEX,
    http_method = HTTP_METHOD_REGEX,
    port = PORT_REGEX,
    url = URL_REGEX,
    protocol = PROTOCOL_REGEX,
    user_agent = USER_AGENT_REGEX,
    http_response_code = HTTP_RETURN_CODE_REGEX,
    referer = REFERER_REGEX,
)


LINE_FILTERS = [
    lambda line: "/revue/" in line and (".html" in line or ".pdf" in line),
    lambda line: "GET" in line,
    lambda line: "200" in line,
]


def interesting_line(log_line):
    return all([filter(log_line) for filter in LINE_FILTERS])


def extract(log_line):
    match = re.match(LOG_REGEX, log_line)

    if match is not None:
        groups = match.groupdict()
        # parse timestamp
        groups["timestamp"] = datetime.strptime(groups["timestamp"], TIMESTAMP_FORMAT)
        groups["http_response_code"] = int(groups["http_response_code"])
        groups["user_agent"] = compute_user_agent(groups["raw_user_agent"])
        groups["second_ip"] = compute_ip_geo_location(groups["second_ip"])
        groups["journal"] = extract_journal(groups["url"])

        return Record(**groups)
    else:
        return None


def extract_journal(url):
    match = re.match(JOURNAL_REGEX, url)

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


def get_ip_info(ip):
    if ip is not None:
        location_string = ", ".join([str(loc) for loc in ip.location]) if ip.location is not None else ""

        return [
            ("user_ip", ip.ip),
            ("continent", ip.continent),
            ("country", ip.country),
            ("geo_coordinates", location_string),
            ("timezone", ip.timezone),
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


def to_csv_row(record):
    return OrderedDict(
        [
            ('time', record.timestamp),
            ('proxy_ip', record.first_ip),
            ('url', record.url),
            ('referer', record.referer),
        ] + \
        get_ip_info(record.second_ip) + \
        [
            ("user_agent", record.raw_user_agent)
        ] + \
        get_user_agent_info(record.user_agent) + \
        get_journal_info(record.journal)
    )

# -*- coding: utf-8 -*-
from __future__ import print_function
import re
from models import *
import codecs
from collections import OrderedDict


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

LOG_REGEX = re.compile("""^(?P<raw_timestamp>{raw_timestamp}) (?P<proxy_ip>{ip}) (?P<http_method>{http_method}) (?P<url>{url}) ({protocol})?- {port} - (?P<user_ip>{ip}) \"(?P<raw_user_agent>{raw_user_agent})\" \"(?P<raw_referer>{raw_referer})\" (?P<http_response_code>{http_response_code}) .+$""".format(
    raw_timestamp = TIMESTAMP_REGEX,
    ip = IP_REGEX,
    http_method = HTTP_METHOD_REGEX,
    port = PORT_REGEX,
    url = URL_REGEX,
    protocol = PROTOCOL_REGEX,
    raw_user_agent = USER_AGENT_REGEX,
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

        return Record(**groups)
    else:
        return None


def get_lines(source_file, encoding = "utf-8"):
    with codecs.open(source_file, "r", encoding=encoding) as f:
        for line in f:
            yield line


def is_pdf_download(record):
    return not record.user_agent.is_bot and record.http_response_code == 200 and record.http_method == "GET"


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

            ('continent', record.continent),
            ('country', record.country),
            ('geo_coordinates', record.geo_coordinates),
            ('timezone', record.timezone),

            ('user_agent', record.raw_user_agent),
            ('browser', record.browser),
            ('os', record.os),
            ('device', record.device),

            ('journal_name', record.journal_name),
            ('publication_year', record.publication_year),
            ('volume', record.volume),
            ('issue', record.issue),
            ('article_id', record.article_id),

            ('age', record.age),
        ]
    )

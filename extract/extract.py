# -*- coding: utf-8 -*-
from __future__ import print_function
import re
from models import *
from datetime import date


TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"
TIMESTAMP_REGEX = "\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
IP_REGEX = "\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
HTTP_METHOD_REGEX = "(GET|POST|HEAD|PUT|DELETE|OPTIONS|TRACE|CONNECT|PROPFIND)"
PORT_REGEX = "\d{1,5}"
URL_REGEX = "[^\s]*"
PROTOCOL_REGEX = "HTTP/1.[01] "
# USER_AGENT_REGEX = '(\"|[^\"\s])*'
USER_AGENT_REGEX = '[^"]*'
REFERER_REGEX = "(\"|[^\"])*"
HTTP_RETURN_CODE_REGEX = "[1-5]\d{2}"

LOG_REGEX = re.compile("""^(?P<raw_timestamp>{raw_timestamp}) (?P<proxy_ip>{ip}) (?P<http_method>{http_method}) (?P<url>{url})\s+({protocol})?- ({port}) - (?P<user_ip>({ip}|-|{ip}, {ip})) \"(?P<raw_user_agent>{raw_user_agent})\" "(?P<raw_referer>{raw_referer})\" (?P<http_response_code>{http_response_code}).+$""".format(
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


def extract(log_line, journal_ref):
    match = LOG_REGEX.match(log_line)

    if match is not None:
        return Record(journal_ref=journal_ref, **match.groupdict())
    else:
        return None


def build_download_list(log_lines, journal_ref, activity_tracker):
    downloads = []
    total = 0
    parsable = 0

    for log_line in log_lines:
        total += 1

        record = extract(log_line, journal_ref)

        if record is not None:
            parsable += 1
            activity_tracker.register_activity(record)

            if record.is_article_download and record.publication_year <= date.today().year:
                downloads.append(record)
        else:
            pass
            # print("=================== cannot parse line")
            # print(log_line)
            # print("===================")

        # remove reference to avoid memory leak
        del record

    return (downloads, total, parsable)

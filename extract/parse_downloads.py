#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from extract import *
from activity_tracker import *
from argument_parsing import *
from common import *
from journals import *
import csv
import multiprocessing as mp
import sys
from collections import namedtuple


LOG_FILE_ENCODING = "us-ascii"


def process_file(params):
    print("Parsing file {}".format(params.log_file))
    download_output_file = "{}.csv".format(params.log_file)

    considered_human = 0

    activity_tracker = ActivityTracker(params.total_number_threshold)

    with codecs.open(download_output_file, "wb") as download_result_file:
        csv_writer = csv.writer(download_result_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        downloads, total, parsable = build_download_list(get_lines(params.log_file, LOG_FILE_ENCODING), activity_tracker)

        for record in downloads:
            is_robot = record.user_ip in activity_tracker.bots_user_ips
            bad_robot = record.user_ip in activity_tracker.bad_bots_user_ips

            if not is_robot:
                considered_human += 1

            if params.keep_robots or (not params.keep_robots and not is_robot):
                csv_writer.writerow(to_byte_string(record.to_csv_row(params.journals)) + [is_robot, bad_robot])

    print(build_result_log(params.log_file, total, parsable, len(downloads), considered_human))

    if params.print_stats_for_ip is not None:
        print(activity_tracker.get_info_for_user_ip(params.print_stats_for_ip))

    if params.verbose:
        print("Good robots user ips: {}".format(len(activity_tracker.good_bots_user_ips)))
        print(" ".join(activity_tracker.good_bots_user_ips))
        print("Bad robots user ips: {}".format(len(activity_tracker.bad_bots_user_ips)))
        print(" ".join(activity_tracker.bad_bots_user_ips))


ProcessFileParam = namedtuple('ProcessFileParam', ['log_file', 'keep_robots',
                                                   'verbose', 'total_number_threshold',
                                                   'journals', 'print_stats_for_ip'])


def build_process_file_param_list(params, journals):
    return [ProcessFileParam(log_file, params.keep_robots,
                             params.verbose, params.total_number_threshold,
                             journals, params.print_stats_for_ip)
            for log_file in params.log_files]


def to_byte_string(row):
    return [unicode(v).encode("utf-8") for v in row]


def write_journals_json_file(journals, journals_file_path, domains_file_path):
    with codecs.open(journals_file_path, "wb") as journals_file:
        csv_writer = csv.writer(journals_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for row in journals.to_journal_csv_rows():
            csv_writer.writerow(to_byte_string(row))

    with codecs.open(domains_file_path, "wb") as domains_file:
        csv_writer = csv.writer(domains_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for row in journals.to_domain_csv_rows():
            csv_writer.writerow(to_byte_string(row))


if __name__ == "__main__":
    params = parse_argv(sys.argv)

    journals = build_journal_referential("journals.json")
    write_journals_json_file(journals, "data/journal.csv", "data/journal-domain.csv")

    # debug mode enables single process execution to have access to stack traces
    if params.debug:
        for param in build_process_file_param_list(params, journals):
            process_file(param)
    else:
        pool = mp.Pool(processes=params.processes)
        # pool.map(process_file, [(log_file, params.keep_robots) for log_file in params.log_files])
        pool.map(process_file, build_process_file_param_list(params, journals))

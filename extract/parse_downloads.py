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

    activity_tracker = ActivityTracker()

    with codecs.open(download_output_file, "w", 'utf-8') as download_result_file:
        csv_writer = csv.writer(download_result_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        downloads, total, parsable = build_download_list(get_lines(params.log_file, LOG_FILE_ENCODING), activity_tracker)

        for record in downloads:
            is_robot = record.user_ip in activity_tracker.get_bots_user_ips

            if not is_robot:
                considered_human += 1

            if params.keep_robots or (not params.keep_robots and not is_robot):
                csv_writer.writerow(record.to_csv_row().values())

    print(build_result_log(params.log_file, total, parsable, len(downloads), considered_human))


ProcessFileParam = namedtuple('ProcessFileParam', ['log_file', 'keep_robots'])


def build_process_file_param_list(params):
    return [ProcessFileParam(log_file, params.keep_robots) for log_file in params.log_files]


if __name__ == "__main__":
    params = parse_argv(sys.argv)

    # debug mode enables single process execution to have access to stack traces
    if params.debug:
        for param in build_process_file_param_list(params):
            process_file(param)
    else:
        pool = mp.Pool(processes=params.processes)
        # pool.map(process_file, [(log_file, params.keep_robots) for log_file in params.log_files])
        pool.map(process_file, build_process_file_param_list(params))

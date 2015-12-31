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

    total = 0
    parsable = 0
    download = 0
    considered_human = 0

    activity_tracker = ActivityTracker()

    with codecs.open(download_output_file, "w", 'utf-8') as download_result_file:
        csv_writer = csv.writer(download_result_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for log_line in get_lines(params.log_file, LOG_FILE_ENCODING):
            total += 1

            record = extract(log_line)

            if record is not None:
                parsable += 1

                if not record.http_response_code == 200 and record.http_method == "GET":
                    continue

                activity_tracker.register_activity(record)

                if record.is_article_download:
                    download += 1

                    if not record.is_good_robot:
                        considered_human += 1

                    if params.keep_robots or (not params.keep_robots and not record.is_good_robot):
                        csv_writer.writerow(record.to_csv_row().values())
            else:
                pass
                # print("=================== cannot parse line")
                # print(log_line)
                # print("===================")

    print(build_result_log(params.log_file, total, parsable, download, considered_human))

    activity_output_file = "{}.activity.csv".format(params.log_file)
    activity_first_line = True


    with codecs.open(activity_output_file, "w", 'utf-8') as activity_result_file:
        csv_writer = csv.writer(activity_result_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for activity in activity_tracker.get_activities():
            # write header using first line data
            if activity_first_line:
                csv_writer.writerow(activity.to_csv_row().keys())
                activity_first_line = False

            csv_writer.writerow(activity.to_csv_row().values())


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

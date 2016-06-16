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
import os


LOG_FILE_ENCODING = "ISO-8859-1"


def process_file_for_process(process_params):
    try:
        return process_file(process_params.params, process_params.log_file, process_params.journals)
    except Exception as e:
        print('Caught exception in worker thread for file {}: {}'.format(process_params.log_file, e))


def process_file(params, log_file, journals):
    print("Parsing file {}".format(log_file))
    download_source_file = "{}/{}".format(params.source_dir, log_file)
    download_output_file = "{}/{}.csv".format(params.output_dir, log_file)
    download_output_file_tmp = "{}.tmp".format(download_output_file)

    considered_human = 0

    activity_tracker = ActivityTracker(params.total_number_threshold)

    with codecs.open(download_output_file_tmp, "wb") as download_result_file:
        csv_writer = csv.writer(download_result_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        downloads, total, parsable = build_download_list(
            get_lines(download_source_file, LOG_FILE_ENCODING),
            journals,
            activity_tracker)

        for record in downloads:
            is_robot = record.user_ip in activity_tracker.bots_user_ips
            bad_robot = record.user_ip in activity_tracker.bad_bots_user_ips

            if not is_robot:
                considered_human += 1

            if params.keep_robots or (not params.keep_robots and not is_robot):
                csv_writer.writerow(to_byte_string(record.to_csv_row(is_robot, bad_robot, params.minimum_fields)))

    # rename file once it's been processed
    os.rename(download_output_file_tmp, download_output_file)

    print(build_result_log(log_file, total, parsable, len(downloads), considered_human))

    if params.print_stats_for_ip is not None:
        print(activity_tracker.get_info_for_user_ip(params.print_stats_for_ip))

    if params.verbose:
        print("Good robots user ips: {}".format(len(activity_tracker.good_bots_user_ips)))
        print(" ".join(activity_tracker.good_bots_user_ips))
        print("Bad robots user ips: {}".format(len(activity_tracker.bad_bots_user_ips)))
        print(" ".join(activity_tracker.bad_bots_user_ips))

    # remove reference to avoid memory leak
    del activity_tracker
    del journals


def to_byte_string(row):
    return [unicode(v).encode("utf-8") for v in row]


def write_journals_json_file(journals, journals_file_path):
    with codecs.open(journals_file_path, "wb") as journals_file:
        csv_writer = csv.writer(journals_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for row in journals.to_csv_rows():
            csv_writer.writerow(to_byte_string(row))


# wraps all arguments that are given to a process
ProcessParam = namedtuple('ProcessParam', ['params', 'log_file', 'journals'])


if __name__ == "__main__":
    params = parse_argv(sys.argv)

    journals = build_journal_referential("journals.json")
    write_journals_json_file(journals, "data/journal.csv")

    # do not process files that have already been processed
    processed_files = [pf[:-4] for pf in get_files(params.output_dir, suffix = ".log.csv", filter=non_emtpy)]
    candidate_files = get_files(params.source_dir, suffix = ".log")
    files_to_process = candidate_files.difference(processed_files)

    if not candidate_files:
        print("Could not find any log file to process")
    elif not files_to_process:
        print("All log files have already been processed")

    # debug mode enables single process execution to have access to stack traces
    if params.debug:
        for log_file in files_to_process:
            process_file(params, log_file, journals)
    else:
        try:
            pool = mp.Pool(processes=params.processes)
            process_parameters = [ProcessParam(params, log_file, journals)
                                  for log_file in files_to_process]

            results = pool.map_async(process_file_for_process, process_parameters).get(timeout=9999999)
        except KeyboardInterrupt:
            pool.terminate()
            pool.join()
        else:
            pool.close()
            pool.join()

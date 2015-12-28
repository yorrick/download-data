#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from extract import *
from argument_parsing import *
from common import *
from journals import *
import csv
import multiprocessing as mp
import sys


LOG_FILE_ENCODING = "us-ascii"


def process_file(log_file):
    print("Parsing file {}".format(log_file))
    output_file = "{}.csv".format(log_file)

    total = 0
    parsable = 0
    download = 0
    first_line = True

    # robot_detector = RobotDetector(detect_downloads_above)

    with codecs.open(output_file, "w", 'utf-8') as result_file:
        result_file.write("sep=,\n")

        csv_writer = csv.writer(result_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for log_line in get_lines(log_file, LOG_FILE_ENCODING):
            total += 1

            record = extract(log_line)

            if record is not None:
                parsable += 1

                if record.is_article_download:
                    download += 1

                    # robot_detector.register_csv_row(csv_row)
                    csv_row = to_csv_row(record)

                    # write header using first line data
                    if first_line:
                        csv_writer.writerow(csv_row.keys())
                        first_line = False

                    csv_writer.writerow(csv_row.values())

    print(build_result_log(log_file, total, parsable, download))


if __name__ == "__main__":
    params = parse_argv(sys.argv)

    # TODO remove this test!!!!
    # process_file(params)

    pool = mp.Pool(processes=4)
    pool.map(process_file, params.log_files)

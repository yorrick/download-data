#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from extract import *
from common import *
import csv
import multiprocessing as mp
import sys


LOG_FILE_ENCODING = "us-ascii"


def process_file(log_file):
    print("Parsing file {}".format(log_file))
    output_file = "{}.csv".format(log_file)

    total = 0
    interesting = 0
    extracted = 0
    download = 0
    first_line = True

    with codecs.open(output_file, "w", 'utf-8') as result_file:
        result_file.write("sep=,\n")

        csv_writer = csv.writer(result_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for log_line in get_lines(log_file, LOG_FILE_ENCODING):
            total += 1

            if interesting_line(log_line):
                interesting += 1
                record = extract(log_line)

                if record is not None:
                    extracted += 1

                    if is_pdf_download(record):
                        download += 1
                        csv_row = to_csv_row(record)

                        # write header using first line data
                        if first_line:
                            csv_writer.writerow(csv_row.keys())
                            first_line = False

                        csv_writer.writerow(csv_row.values())
                else:
                    pass
                    # print(log_line, end="")

    print(build_result_log(log_file, total, interesting, extracted, download))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Give at least one source file")

    log_files = sys.argv[1:]

    pool = mp.Pool(processes=4)
    pool.map(process_file, log_files)

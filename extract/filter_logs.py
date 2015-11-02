#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from extract import *
import csv
import multiprocessing as mp


LOG_FILE_ENCODING = "us-ascii"


def get_ip_info(ip):
    if ip is not None:
        return [ip.ip, ip.continent, ip.country, ip.location, ip.timezone]
    else:
        return ["", "", "", "", ""]


def get_user_agent_info(user_agent):
    if user_agent is not None:
        return [user_agent.browser.family,  # returns 'Mobile Safari'
        user_agent.os.family,  # returns 'iOS'
        user_agent.device.family]  # returns 'iPhone'
    else:
        return ["", "", ""]


def process_file(log_file):
    print("Parsing file {}".format(log_file))
    output_file = "{}.csv".format(log_file)

    total = 0
    interesting = 0
    extracted = 0
    download = 0

    with codecs.open(output_file, "w", LOG_FILE_ENCODING) as result_file:
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

                        row_content = [
                            record.timestamp,
                            record.first_ip,
                            record.url,
                            record.referer,
                        ] + get_ip_info(record.second_ip) + get_user_agent_info(record.user_agent)

                        csv_writer.writerow(row_content)

                else:
                    pass
                    # print(log_line, end="")

    print("Found {} interesting lines ({:4.4f}%) out of {}".format(interesting, (interesting / float(total)) * 100, total))
    print("Extracted {} lines ({:4.4f}%) out of {} interesting".format(extracted, (extracted / float(interesting)) * 100, interesting))
    print("Found {} downloads ({:4.4f}%) out of {} extracted".format(download, (download / float(extracted)) * 100, extracted))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Give at least one source file")

    log_files = sys.argv[1:]

    pool = mp.Pool(processes=4)
    pool.map(process_file, log_files)

# -*- coding: utf-8 -*-
from __future__ import print_function
from optparse import OptionParser


def build_result_log(log_file, total, interesting, extracted, download):
    metrics = {
        "log_file": log_file,
        "total": total,
        "interesting": interesting,
        "interesting_percent": (interesting / float(total)) * 100,
        "extracted": extracted,
        "extracted_percent": (extracted / float(total)) * 100,
        "download": download,
        "download_percent": (download / float(total)) * 100,
    }

    return "{log_file}: Total: {total} => Interesting: {interesting} ({interesting_percent:4.2f}%) => Extracted: {extracted} ({extracted_percent:4.2f}%) => Downloads: {download} ({download_percent:4.2f}%)".format(**metrics)


def build_top_ips_logs(top_ips):
    formatted_top_ips = ["{}: {} => {}".format(ip, count, example_record.values()) for ip, count, example_record in top_ips]
    return "Top ips that downloaded the most:\n{}".format('\n'.join(formatted_top_ips))


class Parameters():
    def __init__(self, log_files, detect_hiding_robots):
        self.log_files = log_files
        self.detect_hiding_robots = detect_hiding_robots

    def __str__(self):
        return "log_files: {}, detect_hiding_robots: {}".format(self.log_files, self.detect_hiding_robots)

    def __repr__(self):
        return str(self)


def parse_argv(argv):
    parser = OptionParser()
    parser.add_option("-d", "--detect-hiding-robots", action="store_true", dest="detect_hiding_robots",
                      help="Attemp to detect hiding robots", default=False)

    (options, args) = parser.parse_args(argv)

    return Parameters(
        log_files=args[1:],
        detect_hiding_robots=options.detect_hiding_robots
    )

# -*- coding: utf-8 -*-
from __future__ import print_function
import argparse
import os.path
import multiprocessing


def is_valid_directory(parser, arg):
    if not os.path.isdir(arg):
        parser.error("The directory %s does not exist!" % arg)
    else:
        return arg


def parse_argv(argv):
    parser = argparse.ArgumentParser(description='Parse filter logs arguments')
    parser.add_argument('--debug', action='store_true', default=False)
    parser.add_argument('--verbose', action='store_true', default=False)
    parser.add_argument('--print-stats-for-ip', dest='print_stats_for_ip')
    parser.add_argument('--keep-robots', dest="keep_robots", action='store_true', default=False)
    parser.add_argument('--processes', dest='processes', type=int, default=multiprocessing.cpu_count(), help="Number of parallel processes to use for log parsing")
    parser.add_argument('--total-number-threshold', dest='total_number_threshold', type=int, default=100, help="Number of requests above which if user did not download any images, and did not ever give a referer, will be considered as a robot")
    parser.add_argument('--minimum-fields', dest="minimum_fields", action='store_true', default=False)
    parser.add_argument("source_dir", help="Directory where log files are stored",
                    type=lambda x: is_valid_directory(parser, x))
    parser.add_argument("output_dir", help="Directory where parsed log files will be written in csv",
                    type=lambda x: is_valid_directory(parser, x))

    return parser.parse_args(argv[1:])

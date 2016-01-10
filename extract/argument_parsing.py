# -*- coding: utf-8 -*-
from __future__ import print_function
import argparse


def parse_argv(argv):
    parser = argparse.ArgumentParser(description='Parse filter logs arguments')
    parser.add_argument('--debug', action='store_true', default=False)
    parser.add_argument('--verbose', action='store_true', default=False)
    parser.add_argument('--keep-robots', dest="keep_robots", action='store_true', default=False)
    parser.add_argument('--processes', dest='processes', type=int, default=4, help="Number of parallel processes to use for log parsing")
    parser.add_argument('--download-number-threshold', dest='download_number_threshold', type=int, default=100, help="Number of download above which if user did not download any images, and did not ever give a referer, will be considered as a robot")
    parser.add_argument('log_files', metavar='F', type=str, nargs='+',
                   help='Name of log files that must be processed')

    return parser.parse_args(argv[1:])

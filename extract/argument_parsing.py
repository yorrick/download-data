# -*- coding: utf-8 -*-
from __future__ import print_function
import argparse


class Parameters():
    def __init__(self, log_files, detect_downloads_above):
        self.log_files = log_files
        self.detect_downloads_above = detect_downloads_above

    def __str__(self):
        return "log_files: {}, detect_downloads_above: {}".format(self.log_files, self.detect_downloads_above)

    def __repr__(self):
        return str(self)


def parse_argv(argv):
    parser = argparse.ArgumentParser(description='Parse filter logs arguments')
    parser.add_argument('--detect-downloads-above', dest='detect_downloads_above', default=None, type=int,
                   help='Detect download above this threshold (in number of downloads)')
    parser.add_argument('log_files', metavar='F', type=str, nargs='+',
                   help='Name of log files that must be processed')

    args = parser.parse_args(argv[1:])

    return Parameters(
        log_files=args.log_files,
        detect_downloads_above=args.detect_downloads_above
    )

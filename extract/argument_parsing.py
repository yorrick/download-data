# -*- coding: utf-8 -*-
from __future__ import print_function
import argparse


def parse_argv(argv):
    parser = argparse.ArgumentParser(description='Parse filter logs arguments')
    parser.add_argument('log_files', metavar='F', type=str, nargs='+',
                   help='Name of log files that must be processed')

    return parser.parse_args(argv[1:])

# -*- coding: utf-8 -*-
from __future__ import print_function
import codecs
from os import listdir, stat
from os.path import isfile, join


def build_result_log(log_file, total, parsable, download, considered_human):
    metrics = {
        "log_file": log_file,
        "total": total,
        "parsable": parsable,
        "parsable_percent": (parsable / float(total)) * 100,
        "download": download,
        "download_percent": (download / float(total)) * 100,
        "considered_human": considered_human,
        "considered_human_percent": (considered_human / float(total)) * 100
    }

    return "{log_file}: Total: {total} => parsable: {parsable} ({parsable_percent:4.2f}%) => download: {download} ({download_percent:4.2f}%) => considered_human: {considered_human} ({considered_human_percent:4.2f}%)".format(**metrics)


def build_top_ips_logs(top_ips):
    formatted_top_ips = ["{}: {}, from proxy ips {}".format(
        detection_result.user_ip,
        detection_result.download_count,
        ", ".join(detection_result.proxy_ips)
    ) for detection_result in top_ips]

    return "Top user ips that downloaded the most:\n{}".format('\n'.join(formatted_top_ips))


class cached_property(object):
    """
    Descriptor (non-data) for building an attribute on-demand on first use.
    """
    def __init__(self, factory):
        """
        <factory> is called such: factory(instance) to build the attribute.
        """
        self._attr_name = factory.__name__
        self._factory = factory

    def __get__(self, instance, owner):
        # Build the attribute.
        attr = self._factory(instance)

        # Cache the value; hide ourselves.
        setattr(instance, self._attr_name, attr)

        return attr


# http://code.activestate.com/recipes/578231-probably-the-fastest-memoization-decorator-in-the-/
def memoize_single_arg(f):
    class memodict(dict):
        __slots__ = ()
        def __missing__(self, key):
            self[key] = ret = f(key)
            return ret

    return memodict().__getitem__


def get_lines(source_file, encoding = "utf-8"):
    with codecs.open(source_file, "r", encoding=encoding) as f:
        for line in f:
            yield line


def get_files(source_dir, suffix, filter=lambda f: True):
    """
    Returns list file inside given directory
    """
    return set([f for f in listdir(source_dir)
                if isfile(join(source_dir, f)) and f.endswith(suffix) and filter(join(source_dir, f))])


def non_emtpy(f):
    statinfo = stat(f)
    return statinfo.st_size > 0

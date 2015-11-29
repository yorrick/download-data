# -*- coding: utf-8 -*-
from __future__ import print_function
from optparse import OptionParser

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"


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
    formatted_top_ips = ["{}: {}, from proxy ips {}".format(
        detection_result.user_ip,
        detection_result.download_count,
        ", ".join(detection_result.proxy_ips)
    ) for detection_result in top_ips]

    return "Top user ips that downloaded the most:\n{}".format('\n'.join(formatted_top_ips))


class Parameters():
    def __init__(self, log_files, detect_downloads_above):
        self.log_files = log_files
        self.detect_downloads_above = detect_downloads_above

    def __str__(self):
        return "log_files: {}, detect_downloads_above: {}".format(self.log_files, self.detect_downloads_above)

    def __repr__(self):
        return str(self)


def parse_argv(argv):
    parser = OptionParser()
    parser.add_option("-r", "--detect-downloads-above", dest="detect_downloads_above",
                  help="Detect download above this threshold", default=None)

    (options, args) = parser.parse_args(argv)

    detect_downloads_above = int(options.detect_downloads_above) if options.detect_downloads_above else None

    return Parameters(
        log_files=args[1:],
        detect_downloads_above=detect_downloads_above
    )


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

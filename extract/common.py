# -*- coding: utf-8 -*-
from __future__ import print_function


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

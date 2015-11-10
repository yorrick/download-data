# -*- coding: utf-8 -*-
from __future__ import print_function


def build_result_log(log_file, total, interesting, extracted, download, downloads_per_user_ip):
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

    number_of_lines_string = "{log_file}: Total: {total} => Interesting: {interesting} ({interesting_percent:4.2f}%) => Extracted: {extracted} ({extracted_percent:4.2f}%) => Downloads: {download} ({download_percent:4.2f}%)".format(**metrics)

    top_ips = sorted(downloads_per_user_ip.items(), key=lambda tup: -tup[1])[:5]
    formatted_top_ips = ["{}: {}".format(ip, count) for ip, count in top_ips]
    top_ips_string = "Top 5 ips that downloaded the most:\n{}".format('\n'.join(formatted_top_ips))

    return "{}\n{}".format(number_of_lines_string, top_ips_string)
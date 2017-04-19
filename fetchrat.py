#!/usr/bin/python3
# TODO: ui & opts, threaded downloads, structure

import sys
import re
import queue
import urllib.request
from Workers import ErrataLinksGatherer


class ReMatchException(Exception): pass


def get_all_errata_pages(current_errata_page):
    errata_re = re.compile('(?:a\s+href\s*=\s*\"\s*'
                           '(?P<errata>\w+\.html)'
                           '\s*\">\s*'
                           '(?P<version>\d\.\d)'
                           's*</a>)')

    try:
        response = urllib.request.urlopen(current_errata_page)
        errata_pages = re.findall(errata_re, response.read().decode())
        if not errata_pages:
            raise ReMatchException
        return errata_pages
    except urllib.request.HTTPError:
        print('Cannot open {} - are you even connected?'.format(current_errata_page))
        sys.exit()


def main():
    home_url = 'http://www.openbsd.org/'

    try:
        all_erratas = get_all_errata_pages(home_url + 'errata.html')
    except ReMatchException:
        print('No match found in response. Exiting.')
        sys.exit()

    work_queue = queue.Queue()
    issue_to_patchurl = {}
    for i in range(7):
        gatherer = ErrataLinksGatherer(work_queue, issue_to_patchurl, home_url)
        gatherer.daemon = True
        gatherer.start()

    for errata_tuple in all_erratas:
        work_queue.put(errata_tuple)
    work_queue.join()


if __name__ == '__main__':
    main()
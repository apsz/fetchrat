#!/usr/bin/python3
# TODO: ui & opts, threaded downloads, structure

import sys
import re
import threading
import queue
import urllib.request


class ReMatchException(Exception): pass


class ErrataLinksGatherer(threading.Thread):

    Dict_Lock = threading.Lock()
    Patch_Name_RE = re.compile(r'(?:<li\s*id\s*=\s*\"\s*(?P<issue_id>.[^\"]*)\">)'
                               r'(?:(?!<p>).)*'
                               r'(?:<a\s*href\s*=\s*\"(?P<patch_url>.[^\"]+?'
                               r'(?:.sig|.patch))\">)',
                               flags=re.DOTALL)

    def __init__(self, work_queue, issue_to_patchurl, home_url):
        super().__init__()
        self.work_queue = work_queue
        self.home_url = home_url
        self.issue_to_patchurl = {}

    def run(self):
        while True:
            try:
                errata_url, version = self.work_queue.get()
                self.process(errata_url, version)
            finally:
                self.work_queue.task_done()

    def process(self, errata_url, version):
        try:
            response = urllib.request.urlopen(self.home_url + errata_url)
            issues_to_patches = re.finditer(ErrataLinksGatherer.Patch_Name_RE, response.read().decode())
            print()
            print(version)
            for match in issues_to_patches:
                print(match.group('issue_id'), match.group('patch_url'))
        except urllib.request.HTTPError as request_err:
            print('Error while reading errata for version {}: {}'.format(version, request_err))


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
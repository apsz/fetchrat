#!/usr/bin/python3


import threading
import re
import urllib.request


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
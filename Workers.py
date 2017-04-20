#!/usr/bin/python3


import os
import re
import urllib.request
import threading


class ErrataLinksGatherer(threading.Thread):

    Patches_Lock = threading.Lock()
    Patch_Name_RE = re.compile(r'(?:<li\s*id\s*=\s*\"\s*(?P<issue_id>.[^\"]*)\">)'
                               r'(?:(?!<p>).)*'
                               r'(?:<a\s*href\s*=\s*\"(?P<patch_url>.[^\"]+?'
                               r'(?:.sig|.patch))\">)',
                               flags=re.DOTALL)

    def __init__(self, work_queue, issue_to_patchurl, home_url):
        super().__init__()
        self.work_queue = work_queue
        self.home_url = home_url
        self.issue_to_patchurl = issue_to_patchurl

    def run(self):
        while True:
            try:
                errata_url, version = self.work_queue.get()
                self.process(errata_url, version)
            finally:
                self.work_queue.task_done()

    def process(self, errata_url, version):
        version_erratas = []
        try:
            response = urllib.request.urlopen(self.home_url + errata_url)
            issues_to_patches = re.finditer(ErrataLinksGatherer.Patch_Name_RE, response.read().decode())
            for match in issues_to_patches:
                version_erratas.append((match.group('issue_id'), match.group('patch_url')))
            with ErrataLinksGatherer.Patches_Lock:
                self.issue_to_patchurl[version] = version_erratas
        except urllib.request.HTTPError as request_err:
            print('Error while reading errata page for version {}: {}'.format(version, request_err))


class DownloaderWorker(threading.Thread):

    def __init__(self, download_queue, result_queue, save_path):
        super().__init__()
        self.download_queue = download_queue
        self.result_queue = result_queue
        self.save_path = save_path or '.'

    def run(self):
        while True:
            try:
                download_url = self.download_queue.get()
                self.process(download_url)
            finally:
                self.download_queue.task_done()

    def process(self, download_url):
        filename = download_url.split('/')[-1]
        try:
            urllib.request.urlretrieve(download_url, os.path.join(self.save_path, filename))
        except (urllib.request.HTTPError, EnvironmentError, IOError) as download_err:
            print('Error while downloading {}: {}'.format(filename, download_err))
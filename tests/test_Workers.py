#!/usr/bin/python3


import os
import unittest
import queue
import urllib.request
import urllib.error
import ssl
import Workers


def add_urllib_https_handler(ssl_protocol):
    protocol_handler = urllib.request.HTTPSHandler(context=ssl.SSLContext(ssl_protocol))
    https_opener = urllib.request.build_opener(protocol_handler)
    urllib.request.install_opener(https_opener)


class TestWorkers(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        add_urllib_https_handler(ssl.PROTOCOL_SSLv23)
        # download Worker
        cls.test_files_to_download = (
            'https://ftp.openbsd.org/pub/OpenBSD/patches/4.7/common/013_pf.patch',
            'https://ftp.openbsd.org/pub/OpenBSD/patches/4.7/common/008_openssl.patch')
        cls.save_path = os.path.dirname(__file__)
        cls.filenames = [(os.path.join(cls.save_path, name.split('/')[-1]))
                          for name in cls.test_files_to_download]
        # gatherer Worker
        cls.home_url = 'https://www.openbsd.org/'
        cls.version_to_errata = [('errata49.html', '4.9')]

    @classmethod
    def tearDownClass(cls):
        for filename in cls.filenames:
            os.remove(filename)

    def test01_download_fail(self):
        download_queue = queue.Queue()
        worker = Workers.DownloaderWorker(download_queue, self.save_path)
        worker.daemon = True
        worker.start()

        for file in self.test_files_to_download:
            download_queue.put(file[:-2])
        self.assertFalse(download_queue.join())
        self.assertFalse(os.path.exists(self.filenames[0]))
        self.assertFalse(os.path.exists(self.filenames[1]))

    def test02_download_success(self):
        download_queue = queue.Queue()
        worker = Workers.DownloaderWorker(download_queue, self.save_path)
        worker.daemon = True
        worker.start()

        for file in self.test_files_to_download:
            download_queue.put(file)
        download_queue.join()
        self.assertTrue(os.path.exists(self.filenames[0]))
        self.assertTrue(os.path.exists(self.filenames[1]))

    def test03_gather_errata_links_fail(self):
        gather_queue = queue.Queue()
        issue_to_patchurl = {}
        gatherer = Workers.ErrataLinksGatherer(gather_queue, issue_to_patchurl,
                                              self.home_url)
        gatherer.daemon = True
        gatherer.start()

        for url, version in self.version_to_errata:
            gather_queue.put((url[:-1], version))
        self.assertFalse(gather_queue.join())

    def test04_gather_errata_links_success(self):
        gather_queue = queue.Queue()
        issue_to_patchurl = {}
        gatherer = Workers.ErrataLinksGatherer(gather_queue, issue_to_patchurl,
                                              self.home_url)
        gatherer.daemon = True
        gatherer.start()

        for url, version in self.version_to_errata:
            gather_queue.put((url, version))
        gather_queue.join()
        self.assertDictEqual(issue_to_patchurl, {'4.9': [('p001_bind',
            'https://ftp.openbsd.org/pub/OpenBSD/patches/4.9/common/001_bind.patch')]})


if __name__ == '__main__':
    unittest.main()
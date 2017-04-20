#!/usr/bin/python3
# TODO: ui & opts, threaded downloads, structure


import os
import sys
import re
import ssl
import queue
import urllib.request
import Workers
import Storage
import CmdUtils


WELCOME_HEADER = 'Fetchrat 0.0.1\nFetching erratas from website...'
UPDATE_DONE = 'Successfully gathered a list of {} patches for {} OpenBSD versions.'
CACHED_FILENAME = 'cached_erratas.xml'


class ReMatchException(Exception): pass


def add_urllib_https_handler(ssl_protocol):
    protocol_handler = urllib.request.HTTPSHandler(context=ssl.SSLContext(ssl_protocol))
    https_opener = urllib.request.build_opener(protocol_handler)
    urllib.request.install_opener(https_opener)


def get_errata_pages(all_erratas_index_url, only_latest_version=True):
    errata_re = re.compile('(?:a\s+href\s*=\s*\"\s*'
                           '(?P<errata>\w+\.html)'
                           '\s*\">\s*'
                           '(?P<version>\d\.\d)'
                           's*</a>)')

    try:
        response = urllib.request.urlopen(all_erratas_index_url)
        errata_pages = re.findall(errata_re, response.read().decode())
        if not errata_pages:
            raise ReMatchException
        return errata_pages
    except urllib.request.HTTPError:
        print('Cannot open {} - are you even connected?'.format(all_erratas_index_url))
        sys.exit()


def fetch_from_website(home_url, only_latest_version=True):
    try:
        add_urllib_https_handler(ssl.PROTOCOL_SSLv23)
        all_erratas = get_errata_pages(home_url + 'errata.html')
    except ReMatchException:
        print('No match found in response. Exiting.')
        sys.exit()

    parse_queue = queue.Queue()
    issue_to_patchurl = {}
    for i in range(7):
        gatherer = Workers.ErrataLinksGatherer(parse_queue, issue_to_patchurl, home_url)
        gatherer.daemon = True
        gatherer.start()

    if only_latest_version:
        all_erratas = (all_erratas[-1],)
    for errata_tuple in all_erratas:
        parse_queue.put(errata_tuple)
    parse_queue.join()

    return issue_to_patchurl


def get_data(use_cashed=False, forced_update_all=False):
    home_url = 'https://www.openbsd.org/'

    if not os.path.exists(CACHED_FILENAME) or forced_update_all:
        return (False, fetch_from_website(home_url, only_latest_version=False))
    if use_cashed:
        return (True, Storage.import_xml_tree())

    cached_data = Storage.import_xml_tree()
    latest_fetched = fetch_from_website(home_url, only_latest_version=True)
    cached_data.update(latest_fetched)
    return (False, cached_data)


def print_list_get_choice(gathered_list, default_max=10):
    for index, version in enumerate(gathered_list):
        num_of_patches = len(gathered_list[version])
        print('{}: {} ({} patch{})'.format(index, version, num_of_patches,
                                           'es' if num_of_patches != 1 else ''))


def main():
    home_url = 'https://www.openbsd.org/'
    print(WELCOME_HEADER)
    used_cached_file, version_to_patches_links = get_data()
    print(UPDATE_DONE.format(sum((len(version_to_patches_links[version])
                                  for version in version_to_patches_links.keys())),
                             len(version_to_patches_links)))
    print_list_get_choice(version_to_patches_links)


if __name__ == '__main__':
    main()
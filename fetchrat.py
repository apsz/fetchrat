#!/usr/bin/python3
# TODO: refactor, list items display limit, auto handling new version
# TODO IDEAS OO? switch to async/aiohttp?


import os
import sys
import re
import ssl
import queue
import argparse
import urllib.request
import Workers
import Storage
import CmdUtils


WELCOME_HEADER = 'Fetchrat 0.0.1\nFetching erratas list...\n'
CACHED_FILENAME = 'cached_erratas.xml'


class ReMatchException(Exception): pass


########################################################################################################################


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

        
def fetch_from_website(home_url, threads_count, only_latest_version=True):
    try:
        all_erratas = get_errata_pages(home_url + 'errata.html')
    except ReMatchException:
        print('No match found in response. Exiting.')
        sys.exit()

    parse_queue = queue.Queue()
    issue_to_patchurl = {}
    for i in range(threads_count):
        gatherer = Workers.ErrataLinksGatherer(parse_queue, issue_to_patchurl, home_url)
        gatherer.daemon = True
        gatherer.start()

    if only_latest_version:
        all_erratas = (all_erratas[-1],)
    for errata_tuple in all_erratas:
        parse_queue.put(errata_tuple)
    parse_queue.join()

    return issue_to_patchurl


def get_data(threads_count, use_cashed=False, forced_update_all=False):
    home_url = 'https://www.openbsd.org/'

    if not os.path.exists(CACHED_FILENAME) or forced_update_all:
        return (False, fetch_from_website(home_url, threads_count, only_latest_version=False))
    if use_cashed:
        return (True, Storage.import_xml_tree())

    cached_data = Storage.import_xml_tree()
    latest_fetched = fetch_from_website(home_url, threads_count, only_latest_version=True)
    cached_data.update(latest_fetched)
    return (False, cached_data)


########################################################################################################################


def print_versions_list_get_choice(version_to_patches):
    versions = []
    print('{:<4} {:<4} {:^12}'.format('#', 'ver.', 'info'))
    print('{0:-<4} {0:-<4} {0:-^12}'.format('-'))
    for index, version in enumerate(version_to_patches):
        versions.append(version)
        num_of_patches = len(version_to_patches[version])
        print('{:<4} {:^4} {:<12}'.format('{}:'.format(index), version,
                                          '{:<} patch{}'.format(num_of_patches,
                                          'es' if num_of_patches != 1 else '')))

    valid = versions + [str(idx) for idx in range(len(versions))] + ['q']
    user_choice = CmdUtils.get_str('Index or version (or "q" to quit)',
                                   input_type='Index or version',
                                   valid=valid, default=versions[-1],
                                   min_len=1, max_len=len(versions[-1]))
    try:
        user_choice = int(user_choice)
        return versions[user_choice]
    except ValueError:
        return user_choice


def download_patches(patch_list, output_path, threads_count):
    download_queue = queue.Queue()
    thread_number = threads_count if (threads_count > len(patch_list)) else len(patch_list)

    for i in range(thread_number):
        downloader = Workers.DownloaderWorker(download_queue, output_path)
        downloader.daemon = True
        downloader.start()

    for patch_url in patch_list:
        download_queue.put(patch_url)
    download_queue.join()
    print('Download complete.')


def get_valid_indexes(index_list, valid, separator=None):
    validation = True
    valid_indexes = []
    for index in index_list:
        index = index.strip()
        if separator and index == separator:
            continue
        if index not in valid:
            print('Invalid index: {}'.format(index))
            return (False, [])
        valid_indexes.append(index)
    return (validation, valid_indexes)


def get_patches_list(patches_to_links, index_list, separator):
    patches_list = []
    if separator == ',':
        for index in index_list:
            patches_list.append(patches_to_links[int(index)][1])
    else:
        for patch in range(int(index_list[0]), int(index_list[-1])+1):
            patches_list.append(patches_to_links[patch][1])
    return patches_list


def print_patches_get_choice(patches_to_links):
    valid_choices = set('c')
    if len(patches_to_links) == 0:
        print('\nNo patches found.\n')
        return 'c'
    print('{:<4} {:<10}'.format('#', 'patch'))
    print('{0:-<4} {0:-<10}'.format('-'))
    for index, (patch_name, patch_link) in enumerate(patches_to_links):
        valid_choices.add(str(index))
        print('{:<4} {:<10}'.format('{}:'.format(index), patch_name))

    while True:
        user_choice = CmdUtils.get_str('Patch index ("-" for range, "," for list, "c" to cancel)',
                                       input_type='Index(es)', min_len=1)
        if user_choice == 'c':
            return user_choice

        separator = None
        for sep in '-,':
            if sep in user_choice:
                user_choice = user_choice.split(sep)
                separator = sep
        if not separator:
            user_choice = [user_choice]

        validation_ok, valid_indexes = get_valid_indexes(user_choice, valid_choices, separator)
        if not validation_ok:
            continue
        patches_list = get_patches_list(patches_to_links, sorted(valid_indexes), separator)
        return patches_list


def get_output_path(default_path='.'):
    while True:
        user_path = CmdUtils.get_str('Set target path ("c" to cancel)', input_type='path',
                                     default='.', min_len=1)
        if os.path.exists(user_path):
            if os.path.isdir(user_path):
                return user_path
            print('Not a valid folder')
            continue
        mkdir_confirmation = CmdUtils.get_str('This folder doesn"t exist, create (y/n)?',
                                              input_type='answer', valid={'y', 'yes', 'no', 'n'},
                                              default='y', min_len=1, max_len=3)
        if mkdir_confirmation in {'y', 'yes'}:
            try:
                os.makedirs(user_path)
                return user_path
            except (OSError, EnvironmentError, IOError) as path_err:
                print('Cannot create folder: {}'.format(path_err))
                continue


########################################################################################################################


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--threads', type=int, default=7,
                        help='Number of threads to run threaded actions with (default: 7, max: 20).')
    grouped = parser.add_mutually_exclusive_group()
    grouped.add_argument('-c', '--cached', action='store_true', default=False,
                         help='Uses previously cached errata file (overriden if no file found).')
    grouped.add_argument('-a', '--download-all', dest='download_all',
                         action='store_true', default=False,
                         help='Forces fetchrat to upload all erratas and patch files based on openbsd'
                              ' website. This is used only when the cached file is not found'
                              ' (by default after first launch). Afterwards the default'
                              'is to only update the new version via network.')
    args = parser.parse_args()
    return args.threads if args.threads < 20 else 7, args.cached, args.download_all


def quit(used_cached_file, current_data):
    if not used_cached_file:
        Storage.export_xml_tree(current_data)
    sys.exit()


def main():
    print(WELCOME_HEADER)
    threads_count, force_cached, force_download = get_args()
    add_urllib_https_handler(ssl.PROTOCOL_SSLv23)
    used_cached_file, version_to_patches = get_data(threads_count, use_cashed=force_cached,
                                                    forced_update_all=force_download)

    while True:
        version_choice_or_quit = print_versions_list_get_choice(version_to_patches)
        if version_choice_or_quit == 'q':
            quit(used_cached_file, version_to_patches)
        patches_list_or_cancel = print_patches_get_choice(version_to_patches[version_choice_or_quit])
        if patches_list_or_cancel == 'c':
            continue
        output_path = get_output_path()
        download_patches(patches_list_or_cancel, output_path, threads_count)


if __name__ == '__main__':
    main()
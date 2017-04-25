#!/usr/bin/python3


import os
import argparse
import ssl
import unittest
import unittest.mock
import fetchrat


class TestFetchrat(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        fetchrat.add_urllib_https_handler(ssl.PROTOCOL_SSLv23)
        cls.cached_erratas_path = os.path.join(os.path.dirname(__file__),
                                               'cached_erratas.xml')
        cls.patches_to_links = [
            ('013_pf.patch',
             'https://ftp.openbsd.org/pub/OpenBSD/patches/4.7/common/013_pf.patch'),
            ('008_openssl.patch',
            'https://ftp.openbsd.org/pub/OpenBSD/patches/4.7/common/008_openssl.patch'),
            ('009_pf.patch',
             'https://ftp.openbsd.org/pub/OpenBSD/patches/4.7/common/009_pf.patch')]
        cls.patch_names = ['013_pf.patch', '008_openssl.patch']

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.cached_erratas_path)

    # get_args()
    def test01_get_args_regular_success(self, *ignore):
        self.assertTupleEqual(fetchrat.get_args(), (7, False, False))

    @unittest.mock.patch('argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(threads=19, cached=False, download_all=True))
    def test02_get_args_regular_success(self, *ignore):
        self.assertTupleEqual(fetchrat.get_args(), (19, False, True))

    @unittest.mock.patch('argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(threads=20, cached=False, download_all=True))
    def test03_get_args_max_threads_exceeded_success(self, *ignore):
        self.assertTupleEqual(fetchrat.get_args(), (7, False, True))

    # erratas: get_data(), fetch_from_website(), get_errata_pages(), Storage.import_xml_tree()
    def test04_update_all_erratas_success(self):
        used_cached, data = fetchrat.get_data(7, False, True)
        with self.assertRaises(SystemExit):
            fetchrat.quit(used_cached, data)
        self.assertFalse(used_cached)
        self.assertTrue(len(data) != 0)
        self.assertTrue(os.path.exists(self.cached_erratas_path))

    def test05_update_newest_errata_success(self):
        used_cached, data = fetchrat.get_data(7, False, False)
        self.assertFalse(used_cached)
        self.assertTrue(len(data) != 0)

    def test06_get_cached_erratas_success(self):
        used_cached, data = fetchrat.get_data(7, use_cashed=True,
                                              forced_update_all=False)
        self.assertTrue(used_cached)
        self.assertTrue(len(data) != 0)

    # print_versions_list_get_choice()
    @unittest.mock.patch('CmdUtils.get_str', return_value='1')
    def test07_get_version_success(self, get_str):
        used_cached, data = fetchrat.get_data(7, use_cashed=True,
                                              forced_update_all=False)
        self.assertEquals(fetchrat.print_versions_list_get_choice(data),
                          '2.2')

    @unittest.mock.patch('CmdUtils.get_str', return_value='2')
    def test08_get_version_fail(self, get_str):
        used_cached, data = fetchrat.get_data(7, use_cashed=True,
                                              forced_update_all=False)
        self.assertNotEquals(fetchrat.print_versions_list_get_choice(data),
                             '2.2')

    # print_patches_get_choice()
    @unittest.mock.patch('CmdUtils.get_str', return_value='2')
    @unittest.mock.patch('fetchrat.get_valid_indexes', return_value=['1', '2'])
    @unittest.mock.patch('fetchrat.get_patches_list', return_value=['https://ftp.openbsd.org/pub/'
                                                                    'OpenBSD/patches/4.7/'
                                                                    'common/008_openssl.patch"',
                                                                    'https://ftp.openbsd.org/pub/'
                                                                    'OpenBSD/patches/4.7/'
                                                                    'common/009_pf.patch'])
    def test09_print_patches_get_choice_success(self, *ignore):
        return_val = fetchrat.print_patches_get_choice(self.patches_to_links)
        self.assertListEqual(return_val, ['https://ftp.openbsd.org/pub/OpenBSD/patches/4.7/'
                                          'common/008_openssl.patch"',
                                          'https://ftp.openbsd.org/pub/OpenBSD/patches/4.7/'
                                           'common/009_pf.patch'])

    @unittest.mock.patch('CmdUtils.get_str', return_value='c')
    def test10_print_patches_get_choice_cancel_success(self, *ignore):
        return_val = fetchrat.print_patches_get_choice(self.patches_to_links)
        self.assertEquals(return_val, 'c')

    # get_valid_indexes()
    def test11_get_valid_index_success(self):
        assertion, valid_indexes = fetchrat.get_valid_indexes(['1', ',', '2'],
                                                              ['1', '2', '3'],
                                                              ',')
        self.assertTrue(assertion)
        self.assertListEqual(valid_indexes, ['1', '2'])


    def test12_get_valid_index_fail(self):
        assertion, valid_indexes = fetchrat.get_valid_indexes(['1', ',', '2'],
                                                              ['1', '2', '3'],
                                                              '.')
        self.assertFalse(assertion)
        self.assertListEqual(valid_indexes, [])

    # get_patches_list()
    def test13_get_patches_list_success(self):
        patches_list = fetchrat.get_patches_list(self.patches_to_links, ['0', '1'], ',')
        self.assertListEqual(patches_list, ['https://ftp.openbsd.org/pub/'
                                            'OpenBSD/patches/4.7/common/013_pf.patch',
                                            'https://ftp.openbsd.org/pub/'
                                            'OpenBSD/patches/4.7/common/008_openssl.patch'])

    def test14_get_patches_list_fail(self):
        patches_list = fetchrat.get_patches_list(self.patches_to_links, ['1', '2'], ',')
        self.assertNotEqual(patches_list, ['https://ftp.openbsd.org/pub/'
                                            'OpenBSD/patches/4.7/common/013_pf.patch',
                                            'https://ftp.openbsd.org/pub/'
                                            'OpenBSD/patches/4.7/common/008_openssl.patch'])

    def test15_get_patches_list_range_success(self):
        patches_list = fetchrat.get_patches_list(self.patches_to_links, ['0', '2'], '-')
        self.assertListEqual(patches_list, ['https://ftp.openbsd.org/pub/'
                                            'OpenBSD/patches/4.7/common/013_pf.patch',
                                            'https://ftp.openbsd.org/pub/'
                                            'OpenBSD/patches/4.7/common/008_openssl.patch',
                                            'https://ftp.openbsd.org/pub/'
                                            'OpenBSD/patches/4.7/common/009_pf.patch'])

    def test16_get_patches_list_range_fail(self):
        patches_list = fetchrat.get_patches_list(self.patches_to_links, ['0', '2'], '-')
        self.assertNotEqual(patches_list, ['https://ftp.openbsd.org/pub/'
                                           'OpenBSD/patches/4.7/common/013_pf.patch',
                                           'https://ftp.openbsd.org/pub/'
                                           'OpenBSD/patches/4.7/common/009_pf.patch'])

    # get_output_path()
    @unittest.mock.patch('CmdUtils.get_str', return_value='output_folder')
    @unittest.mock.patch('os.path.exists', return_value=True)
    @unittest.mock.patch('os.path.isdir', return_value=True)
    def test17_get_output_path_found_success(self, *ignore):
        user_path = fetchrat.get_output_path()
        self.assertEqual(user_path, 'output_folder')


if __name__ == '__main__':
    unittest.main()


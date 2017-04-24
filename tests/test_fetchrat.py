#!/usr/bin/python3


import os
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

    def test01_update_all_erratas_success(self):
        used_cached, data = fetchrat.get_data(7, False, True)
        with self.assertRaises(SystemExit):
            fetchrat.quit(used_cached, data)
        self.assertFalse(used_cached)
        self.assertTrue(len(data) != 0)
        self.assertTrue(os.path.exists(self.cached_erratas_path))

    def test02_update_newest_errata_success(self):
        used_cached, data = fetchrat.get_data(7, False, False)
        self.assertFalse(used_cached)
        self.assertTrue(len(data) != 0)

    def test03_get_cached_erratas_success(self):
        used_cached, data = fetchrat.get_data(7, use_cashed=True,
                                              forced_update_all=False)
        self.assertTrue(used_cached)
        self.assertTrue(len(data) != 0)

    @unittest.mock.patch('CmdUtils.get_str', return_value='1')
    def test04_get_version_success(self, get_str):
        used_cached, data = fetchrat.get_data(7, use_cashed=True,
                                              forced_update_all=False)
        self.assertEquals(fetchrat.print_versions_list_get_choice(data),
                          '2.2')

    @unittest.mock.patch('CmdUtils.get_str', return_value='2')
    def test04_get_version_fail(self, get_str):
        used_cached, data = fetchrat.get_data(7, use_cashed=True,
                                              forced_update_all=False)
        self.assertNotEquals(fetchrat.print_versions_list_get_choice(data),
                             '2.2')

    def test05_get_valid_index_success(self):
        assertion, valid_indexes = fetchrat.get_valid_indexes(['1', ',', '2'],
                                                              ['1', '2', '3'],
                                                              ',')
        self.assertTrue(assertion)
        self.assertListEqual(valid_indexes, ['1', '2'])


    def test06_get_valid_index_fail(self):
        assertion, valid_indexes = fetchrat.get_valid_indexes(['1', ',', '2'],
                                                              ['1', '2', '3'],
                                                              '.')
        self.assertFalse(assertion)
        self.assertListEqual(valid_indexes, [])

    def test07_get_patches_list_success(self):
        patches_list = fetchrat.get_patches_list(self.patches_to_links, ['0', '1'], ',')
        self.assertListEqual(patches_list, ['https://ftp.openbsd.org/pub/'
                                            'OpenBSD/patches/4.7/common/013_pf.patch',
                                            'https://ftp.openbsd.org/pub/'
                                            'OpenBSD/patches/4.7/common/008_openssl.patch'])

    def test08_get_patches_list_fail(self):
        patches_list = fetchrat.get_patches_list(self.patches_to_links, ['1', '2'], ',')
        self.assertNotEqual(patches_list, ['https://ftp.openbsd.org/pub/'
                                            'OpenBSD/patches/4.7/common/013_pf.patch',
                                            'https://ftp.openbsd.org/pub/'
                                            'OpenBSD/patches/4.7/common/008_openssl.patch'])

    def test09_get_patches_list_range_success(self):
        patches_list = fetchrat.get_patches_list(self.patches_to_links, ['0', '2'], '-')
        self.assertListEqual(patches_list, ['https://ftp.openbsd.org/pub/'
                                            'OpenBSD/patches/4.7/common/013_pf.patch',
                                            'https://ftp.openbsd.org/pub/'
                                            'OpenBSD/patches/4.7/common/008_openssl.patch',
                                            'https://ftp.openbsd.org/pub/'
                                            'OpenBSD/patches/4.7/common/009_pf.patch'])

    def test10_get_patches_list_range_fail(self):
        patches_list = fetchrat.get_patches_list(self.patches_to_links, ['0', '2'], '-')
        self.assertNotEqual(patches_list, ['https://ftp.openbsd.org/pub/'
                                           'OpenBSD/patches/4.7/common/013_pf.patch',
                                           'https://ftp.openbsd.org/pub/'
                                           'OpenBSD/patches/4.7/common/009_pf.patch'])

    @unittest.mock.patch('CmdUtils.get_str', return_value='2')
    @unittest.mock.patch('fetchrat.get_valid_indexes', return_value=['1', '2'])
    @unittest.mock.patch('fetchrat.get_patches_list', return_value=['https://ftp.openbsd.org/pub/'
                                                                    'OpenBSD/patches/4.7/'
                                                                    'common/008_openssl.patch"',
                                                                    'https://ftp.openbsd.org/pub/'
                                                                    'OpenBSD/patches/4.7/'
                                                                    'common/009_pf.patch'])
    def test11_print_patches_get_choice_success(self, *ignore):
        return_val = fetchrat.print_patches_get_choice(self.patches_to_links)
        self.assertListEqual(return_val, ['https://ftp.openbsd.org/pub/OpenBSD/patches/4.7/'
                                          'common/008_openssl.patch"',
                                          'https://ftp.openbsd.org/pub/OpenBSD/patches/4.7/'
                                           'common/009_pf.patch'])

    @unittest.mock.patch('CmdUtils.get_str', return_value='c')
    def test12_print_patches_get_choice_cancel_success(self, *ignore):
        return_val = fetchrat.print_patches_get_choice(self.patches_to_links)
        self.assertEquals(return_val, 'c')


if __name__ == '__main__':
    unittest.main()


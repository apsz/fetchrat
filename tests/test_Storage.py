#!/usr/bin/python3


import os
import unittest
import collections
import Storage


def create_test_data(valid=True):
    versions = ['2.2', '5.1', '4.2', '6.1']
    patchnames = [c for c in 'qwertyuiop']
    patchlinks = [l for l in map(str, range(len(patchnames)))]

    data = collections.OrderedDict()
    for version in versions:
        if valid:
            data[version] = []
        for name, url in zip(patchnames, patchlinks):
            if valid:
                data[version].append((name, url))
            else:
                data[version] = (name, url)
    return data


class TestStorage(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.valid_data = create_test_data()
        cls.invalid_data = create_test_data(valid=False)
        cls.output_filename = os.path.join(os.path.dirname(__file__),
                                            'cached_erratas.xml')

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.output_filename)

    def test01_export_xml_fail(self):
        with self.assertRaises(IndexError):
            self.assertFalse(Storage.export_xml_tree(self.invalid_data))
            self.assertFalse(os.path.exists(self.output_filename))

    def test02_import_xml_fail(self):
        self.assertFalse(Storage.import_xml_tree())

    def test03_export_xml_success(self):
        self.assertTrue(Storage.export_xml_tree(self.valid_data))
        self.assertTrue(os.path.exists(self.output_filename))

    def test04_import_xml_success(self):
        self.assertDictEqual(dict(Storage.import_xml_tree()), dict(self.valid_data))


if __name__ == '__main__':
    unittest.main()
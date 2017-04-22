#!/usr/bin/python3


import os
import sys
import xml
import collections
from xml.etree import ElementTree
from xml.parsers.expat import ExpatError


PATCH_NAME, PATCH_URL = range(2)


def export_xml_tree(data):
    root = xml.etree.ElementTree.Element('versions')
    for version in sorted(data.keys(), key=float):
        version_patches = xml.etree.ElementTree.Element('version',
                                                        version=version)
        for patch in data[version]:
            patch_name = xml.etree.ElementTree.SubElement(version_patches, 'patch_name')
            patch_name.text = patch[PATCH_NAME]
            patch_url = xml.etree.ElementTree.SubElement(patch_name, 'patch_url')
            patch_url.text = patch[PATCH_URL]
        root.append(version_patches)
    tree = xml.etree.ElementTree.ElementTree(root)
    try:
        tree.write('cached_erratas.xml', 'UTF-8')
        return True
    except (IOError, EnvironmentError, xml.parsers.expat.ExpatError) as export_err:
        print('{} error: {}'.format(os.path.basename(sys.argv[0]), export_err))
        return False


def import_xml_tree():
    try:
        data = xml.etree.ElementTree.parse('cached_erratas.xml')
    except (IOError, EnvironmentError, xml.parsers.expat.ExpatError) as import_err:
        print('{} error: {}'.format(os.path.basename(sys.argv[0]), import_err))
        return False

    cached_data = collections.OrderedDict()

    try:
        for version in data.findall('version'):
            version_patches = []
            for patch in version.findall('patch_name'):
                patch_url = patch.find('patch_url').text
                version_patches.append((patch.text, patch_url))
            cached_data[version.get('version')] = version_patches
        return cached_data
    except (xml.parsers.expat.ExpatError) as import_err:
        print('Error: {}'.format(import_err))
        return False


if __name__ == '__main__':
    print(import_xml_tree())
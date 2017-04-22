#!/usr/bin/python3

import ssl
import certifi
import urllib.request
import urllib.response
import requests

# response = requests.get('https://ftp.openbsd.org/pub/OpenBSD/patches/6.0/common/020_exec_elf.patch.sig')
# print(response.text)
url = 'https://ftp.openbsd.org/pub/OpenBSD/patches/6.0/common/020_exec_elf.patch.sig'
# response = urllib.request.urlopen(url.replace(':', '%3A'))
# print(response.read())

# class HTTPS_Handler:
#
#     def __init__(self, protocol):
#         self.protocol = protocol
#
#     def __enter__(self):
#         https_sslv23_handler = urllib.request.HTTPSHandler(context=ssl.SSLContext(self.protocol))
#         self.https_opener = urllib.request.build_opener(https_sslv23_handler)
#         urllib.request.install_opener(self.https_opener)
#         # return self.https_opener
#
#     def __exit__(self, *ignore):
#         self.https_opener.close()
#
# with HTTPS_Handler(ssl.PROTOCOL_SSLv23):
#     urllib.request.urlretrieve(url, 'test')
filename = url.split('/')[-1]
#filename = urllib.request.urlsplit(url)
print(filename)

#urllib.request.urlopen(url)
    # response = https_opener.open(url)
    # print(response.read())

# print(ssl._PROTOCOL_NAMES)
# https_sslv23_handler = urllib.request.HTTPSHandler(context=ssl.SSLContext(ssl.PROTOCOL_SSLv23))
# opener = urllib.request.build_opener(https_sslv23_handler)
# urllib.request.install_opener(opener)
# resp = opener.open(url)
# html = resp.read().decode('utf-8')
# print(html)
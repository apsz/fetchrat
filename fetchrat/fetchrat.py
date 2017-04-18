#!/usr/env python3

import urllib.request

response = urllib.request.urlopen('http://python.kofeina.net/')
print(response.read())
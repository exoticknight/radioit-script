#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import sys
import argparse
import re
import urlparse

from bs4 import BeautifulSoup


def mms_extract(url):
    try:
        soup = BeautifulSoup(urllib2.urlopen(url, timeout=60), "html.parser")
        return soup.select("ref")[0]["href"]
    except Exception, e:
        return "Network Error."


def loop_asx(asxs):
    for asx in asxs:
        if asx[-4:] != ".asx":
            print("{} is not asx file".format(asx))
        else:
            print("Processing {} ...".format(asx))
            print mms_extract(asx)


def process(option):
    if option.analyse:
        # analyse wepage
        url = option.urls[0] # only process the first one
        soup = BeautifulSoup(urllib2.urlopen(url, timeout=60), "html.parser")
        a = soup.find_all(href=re.compile(".*\.asx"))
        if a:
            loop_asx([urlparse.urljoin(url, x["href"]) for x in a])
    else:
        loop_asx(option.urls)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(version="1.0")
    parser.add_argument("-a", "--analyse", action="store_true", dest="analyse", help="try to analyse .asx in a webpage")
    parser.add_argument("urls", action="store", nargs="+", help="urls of .asx file")

    try:
        args = parser.parse_args(sys.argv[1:])
    except argparse.ArgumentError, e:
        print("bad options: {0}".format(e))
    except argparse.ArgumentTypeError, e:
        print("bad option value: {0}".format(e))
    else:
        process(args)
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import urllib2
import sys
import argparse


def get_file_name(url):
    return url.split("/")[-1]


def mms_extract(url):
    soup = BeautifulSoup(urllib2.urlopen(url))
    return soup.select("ref")[0]["href"]


def print_info(soup):
    try:
        print(soup.select("#hbkProgramText > div")[-5].select("span")[0].string)
    except Exception, e:
        print(soup.select(".hbkDescriptonContents")[-1].previous_sibling.previous_sibling.previous_sibling.previous_sibling.select("span")[0].string)


def print_description(soup):
    d_contents = soup.select("table.hbkTextTable td:nth-of-type(1) div:nth-of-type(3) table:nth-of-type(2) td")
    if d_contents:
        print(d_contents[0].get_text().encode("gb18030"))
    else:
        print("no description")


def download_audio(soup):
    mms = soup.select("div.hbkDescriptonContents embed")[-1]["src"]
    print(mms_extract(mms))


def download_images(soup):
    image = soup.select("table.hbkTextTable td:nth-of-type(1) div:nth-of-type(3) table:nth-of-type(2) td img")
    if image:
        import urllib
        urllib.urlretrieve(image[0]["src"], filename=get_file_name(image[0]["src"]))
        print("done")
    else:
        print("no image")


def process(option, *args, **kwargs):
    print("processing...{0}".format(option.name))

    try:
        soup = BeautifulSoup(urllib2.urlopen(u"http://hibiki-radio.jp/description/{name}".format(name=option.name), timeout=30))
    except Exception, e:
        print("network error.")
        return
    
    print("---------------------infomation--------------------")
    print_info(soup)
    
    if option.description or option.complete:
        print("--------------------description--------------------")
        try:
	        print_description(soup)
        except Exception, e:
	        print(e)
    
    if option.image or option.complete:
        print("-----------------------image-----------------------")
        try:
            download_images(soup)
        except Exception, e:
            print("failed")

    if option.audio or option.complete:
        print("-----------------------audio-----------------------")
        try:
            download_audio(soup)
        except Exception, e:
            print("failed")

    print("---------------------------------------------------")
    print("Completed.")
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(version="1.0")

    parser.add_argument("-i", "--image", action="store_true", dest="image", help="download iamge")
    parser.add_argument("-a", "--audio", action="store_true", dest="audio", help="download audio")
    parser.add_argument("-d", "--description", action="store_true", dest="description", help="show description")
    parser.add_argument("-c", "--complete", action="store_true", dest="complete", help="perform all operation")
    parser.add_argument("name", action="store", help="bangumi name")

    try:
        args = parser.parse_args(sys.argv[1:])
    except argparse.ArgumentError, e:
        print("bad options: {0}".format(e))
    except argparse.ArgumentTypeError, e:
        print("bad option value: {0}".format(e))
    else:
        process(args)
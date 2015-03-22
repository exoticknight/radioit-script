#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import argparse
import urllib2
import sys
import json


def get_file_name(url):
    return url.split("/")[-1]


def print_info(soup):
    info = soup.select("#newProgramWrap h1")[0]
    print(info.get_text())


def print_description(soup):
    d_contents = soup.select(".newProgramRight p")
    if d_contents:
        print(d_contents[0].get_text().encode("gb18030"))
    else:
        print("no description")


def download_audio(name, proxy):

    print("collecting information...")
    try:
        respose = urllib2.urlopen(u"http://www.onsen.ag/data/api/getMovieInfo/{name}".format(name=name), timeout=60)
        bangumi = json.loads((respose.read())[9:-3])
    except Exception, e:
        print("Error:{0}".format(e))
        return

    path = bangumi["moviePath"]["pc"]
    filename = get_file_name(path)
    print(path)

    print("downloading...")
    if proxy is None:
        import urllib
        urllib.urlretrieve(path, filename=filename)
    else:
        if proxy[0] == "http":
            # not sure whether this works...
            import urllib
            urllib.request.install_opener(urllib.request.build_opener(urllib.request.ProxyHandler({"http": proxy[1]})))
            urllib.request.urlretrieve(path, filename=filename)
        elif proxy[0] == "socks":
            proxy_ip, proxy_port = proxy[1].split(":")
            import socks
            import socket
            socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, proxy_ip, int(proxy_port))
            socket.socket = socks.socksocket
            import urllib
            urllib.urlretrieve(path, filename=filename)


def download_images(soup, name):
    for pic in soup.select(".newProgramLeft > img"):
        path = pic["src"]
        filename = get_file_name(path)
        import urllib
        urllib.urlretrieve(u"http://www.onsen.ag/program/{name}/".format(name=name) + path, filename=filename)
        print("done")


def process(option, proxy):
    print("processing...{0}".format(option.name))
    
    soup = BeautifulSoup(urllib2.urlopen(u"http://www.onsen.ag/program/{name}/".format(name=option.name), timeout=60))
    
    print("---------------------infomation--------------------")
    print_info(soup)
    
    if option.description or option.complete:
        print("--------------------description--------------------")
        try:
            print_description(soup)
        except Exception, e:
            print("failed")

    if option.image or option.complete:
        print("-----------------------image-----------------------")
        try:
            download_images(soup, option.name)
        except Exception, e:
            print("failed")

    if option.audio or option.complete:
        print("-----------------------audio-----------------------")
        try:
            download_audio(option.name, proxy)
        except Exception, e:
            print("failed, error {0}".format(e))

    print("---------------------------------------------------")
    print("Completed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(version="1.0")

    parser.add_argument("-i", "--image", action="store_true", dest="image", help="download images")
    parser.add_argument("-a", "--audio", action="store_true", dest="audio", help="download audio")
    parser.add_argument("-d", "--description", action="store_true", dest="description", help="show description")
    parser.add_argument("-c", "--complete", action="store_true", dest="complete", help="perform all operation")
    parser.add_argument("-p", "--proxy", nargs=2, action="store", dest="proxy", help="set the proxy address", metavar=("http/socks", "PROXY_ADDRESS"))
    parser.add_argument("name", action="store", help="list of bangumi name, name")

    SUPPORT_PROXY = set(["http", "socks"])

    try:
        args = parser.parse_args(sys.argv[1:])
    except argparse.ArgumentError, e:
        print("bad options: {0}".format(e))
    except argparse.ArgumentTypeError, e:
        print("bad option value: {0}".format(e))
    else:
        if not args.proxy:
            process(args, None)
        else:
            if args.proxy[0] not in SUPPORT_PROXY:
                print("proxy type {0} is not supported!".format(args.proxy[0]))
            else:
                process(args, args.proxy)
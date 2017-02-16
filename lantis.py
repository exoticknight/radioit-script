#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import sys
import argparse
import urlparse

from functools import wraps
from bs4 import BeautifulSoup

__debug = False
__codes = {
    "win32": "gb18030"
}.get(sys.platform, "utf8")


"""utils
"""
def handle_error(e, message):
    print(message)

    global __debug
    if __debug:
        print("-" * 15)
        print(e)


def prettify_table(table, separator=" "):
    max_width = [max(len(x) for x in col) for col in zip(*table)]
    line_list = [
        separator.join( \
            u"{0}".format(x) if i == len(line) - 1 else u"{0:{width}}".format(x, width=max_width[i]) \
                for i, x in enumerate(line) \
            ) \
        for line in table]
    return u"\n".join(line_list)


"""command: list
        self-defined functions can be called by arguments after 'list' command
"""
def list_all():

    # acquire html content
    try:
        soup = BeautifulSoup(urllib2.urlopen(u"http://lantis-net.com/", timeout=60), "html.parser")
    except Exception, e:
        handle_error(e, "Network Error.")
        return

    content = [a.find("a") for a in soup.select(".titles")]

    # prepare report text
    table = [(u"ID", u"Name")] + [(a["href"][22:-1], a.get_text()) for a in content]
    # prettify table
    text = prettify_table(table)

    print(text.encode(__codes))
    print("\n{0} bangumi counted.".format(len(table) - 1))


def list_daily(day):
    from datetime import date
    day_selector = {
        0: 'mon',
        1: 'tue',
        2: 'wed',
        3: 'thu',
        4: 'fri',
        5: 'sat',
        6: 'sun'
    }.get(date.weekday(date.today()) if not day else day[0] - 1, None) # 0 stands for monday in time module

    if not day_selector:
        print("Nothing found.")
        return

    # acquire html content
    try:
        soup = BeautifulSoup(urllib2.urlopen(u"http://lantis-net.com/contents/{}.html".format(day_selector), timeout=60), "html.parser")
    except Exception, e:
        handle_error(e, "Network Error.")
        return

    content = soup.select("div[class^=joho] > a")

    if not content:
        print("Nothing found.")
        return

    # prepare report text
    table = [(u"Status", u"ID", u"Name")]

    table += [(u"Normal", p["href"][22:-1], p.find("img")["alt"]) for p in content]

    # prettify table
    text = prettify_table(table)

    print(text.encode(__codes))
    print("\n{0} bangumi counted.".format(len(table) - 1))


def list_new():
    print("Not supported.")


def process(option):

    global __debug
    __debug = option.debug

    if option.sp_name == "list":
        # write your handle for command 'list' below
        # ....

        # handle arguments, fill the IF block
        if option.today:
            # self-definded function for listing out today's bangumi
            list_daily(0)

        elif option.day:
            # self-definded function for listing out bangumi of specific day
            list_daily(option.day)

        elif option.new:
            # self-definded function for listing out recent new bangumi / updated bangumi
            list_new()

        elif option.all:
            # self-definded function for listing out all bangumi
            list_all()

    elif option.sp_name == "download":
        # handle arguments, fill the IF block
        if option.everything or option.image:
            # self-defined function for downloading bangumi image
            print("Not supported.")

        if option.everything or option.audio:
            # self-defined function for downloading bangumi image
            print("Please use 'python asx_extractor.py -a " + u"http://lantis-net.com/{id}".format(id=option.id) +"' to download audio.")

    elif option.sp_name == "show":
        print("Please go to " + u"http://lantis-net.com/{id}".format(id=option.id) + " for more information.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(version="2.0")
    parser.add_argument("--debug", action="store_true", dest="debug", default=False, help="debug mode")
    sp = parser.add_subparsers(title="commands", description="support commands", help="what they will do", dest="sp_name")

    # command 'list'
    #
    # Args:
    #   -a, --all: all bangumi
    #   -n, --new: new bangumi
    #   --today: today's bangumi
    #   -d day, --day day: bangumi of specifical day
    sp_list = sp.add_parser("list", help="list bangumi")
    action = sp_list.add_mutually_exclusive_group(required=True)
    action.add_argument("-a", "--all", action="store_true", dest="all", help="all bangumi")
    action.add_argument("-n", "--new", action="store_true", dest="new", help="new bangumi")
    action.add_argument("--today", action="store_true", dest="today", help="today's bangumi")
    action.add_argument("-d", "--day", action="store", dest="day", nargs=1, metavar="day", type=int, choices=range(1,8), help="bangumi of specifical day")

    # command 'download'
    #
    # Args:
    #   -a, --audio: download audio
    #   -i, --image: download image
    #   -p, --proxy: set proxy address
    #   -e, --everything: download audio and image
    #   id: bangumi id, usually not the real name of the bangumi but a string
    sp_download = sp.add_parser("download", help="download bangumi")
    sp_download.add_argument("-a", "--audio", action="store_true", dest="audio", help="including audio")
    sp_download.add_argument("-i", "--image", action="store_true", dest="image", help="including image")
    # sp_download.add_argument("-p", "--proxy", nargs=2, action="store", dest="proxy", help="set the proxy address", metavar=("http/socks", "PROXY_ADDRESS"))
    sp_download.add_argument("-e", "--everything", action="store_true", dest="everything", help="including everything")
    sp_download.add_argument("id", action="store", default=None, help="bangumi id")

    # command 'show'
    #
    # Args:
    #   -n, --name: bangumi name
    #   -d, --description: description of the bangumi
    #   -t, --title: episode title
    #   -c, --comment: comment that will be updated each episode
    #   -s, --schedule: schedule of the bangumi
    #   -p, --personality: host of the bangumi
    #   -g, --guest: guest of the bangumi
    #   -v, --verbose: verbose mode, show everything
    #   id: bangumi id, usually not the real name of the bangumi but a string
    sp_show = sp.add_parser("show", help="show details")
    sp_show.add_argument("-n", "--name", action="store_true", dest="name", help="including name")
    sp_show.add_argument("-d", "--description", action="store_true", dest="description", help="including description")
    sp_show.add_argument("-t", "--title", action="store_true", dest="title", help="episode title")
    sp_show.add_argument("-c", "--comment", action="store_true", dest="comment", help="including comment")
    sp_show.add_argument("-s", "--schedule", action="store_true", dest="schedule", help="including updated schedule")
    sp_show.add_argument("-p", "--personality", action="store_true", dest="personality", help="including personality")
    sp_show.add_argument("-g", "--guest", action="store_true", dest="guest", help="including guest")
    sp_show.add_argument("-v", "---verbose", action="store_true", dest="verbose", help="verbose mode")
    sp_show.add_argument("id", action="store", default=None, help="bangumi id")

    try:
        args = parser.parse_args(sys.argv[1:])
    except argparse.ArgumentError, e:
        print("bad options: {0}".format(e))
    except argparse.ArgumentTypeError, e:
        print("bad option value: {0}".format(e))
    else:
        process(args)
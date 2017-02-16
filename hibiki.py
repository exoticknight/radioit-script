#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import time
import urllib2
import argparse
import urlparse

from functools import wraps
from bs4 import BeautifulSoup

__debug = False
__codes = {
    "win32": "gb18030"
}.get(sys.platform, "utf8")
request_headers = {
    "Host": "vcms-api.hibiki-radio.jp",
    "Connection": "keep-alive",
    "Accept": "application/json, text/plain, */*",
    "Origin": "http://hibiki-radio.jp",
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36",
    "DNT": "1",
    "Referer": "http://hibiki-radio.jp/",
    "Accept-Encoding": "gzip, deflate, sdch",
    "Accept-Language": "en-US,en;q=0.8"
}

"""utils
"""
def load_cache():
    pass

def save_cache():
    pass

def handle_error(e, message):
    print(message)

    global __debug
    if __debug:
        print("-" * 15)
        print(e)


def get_file_name(url):
    return url.split("/")[-1]


def mms_extract(url):
    soup = BeautifulSoup(urllib2.urlopen(url), "html.parser")
    return soup.select("ref")[0]["href"]


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
def list_all(bangumis):
    # prepare report text
    upd_table = [("Update", b["access_id"], b["name"]) for b in bangumis if b["update_flg"]]
    new_table = [("New", b["access_id"], b["name"]) for b in bangumis if b["new_program_flg"]]
    nor_table = [("Normal", b["access_id"], b["name"]) for b in bangumis if not b["update_flg"] and not b["new_program_flg"]]
    table = [(u"Status", u"ID", u"Name")] + upd_table + new_table + nor_table

    # prettify table
    text = prettify_table(table)

    print(text.encode(__codes))
    print("\n{0} bangumi counted.".format(len(table) - 1))


def list_daily(day, bangumis):
    from datetime import date
    day_of_week = [date.weekday(date.today()),1,2,3,4,5,6,6][day]

    day_bangumi = [b for b in bangumis if b["day_of_week"] == day_of_week]

    if not day_bangumi:
        print("Nothing found.")
        return

    # prepare report text
    upd_table = [("Update", b["access_id"], b["name"]) for b in day_bangumi if b["update_flg"]]
    new_table = [("New", b["access_id"], b["name"]) for b in day_bangumi if b["new_program_flg"]]
    nor_table = [("Normal", b["access_id"], b["name"]) for b in day_bangumi if not b["update_flg"] and not b["new_program_flg"]]
    table = [(u"Status", u"ID", u"Name")] + upd_table + new_table + nor_table

    # prettify table
    text = prettify_table(table)

    print(text.encode(__codes))
    print("\n{0} bangumi counted.".format(len(table) - 1))


def list_new(bangumis):
    # prepare report text
    upd_table = [("Update", b["access_id"], b["name"]) for b in bangumis if b["update_flg"]]
    new_table = [("New", b["access_id"], b["name"]) for b in bangumis if b["new_program_flg"]]
    table = [(u"Status", u"ID", u"Name")] + upd_table + new_table

    # prettify table
    text = prettify_table(table)

    print(text.encode(__codes))
    print("\n{0} bangumi counted.".format(len(table) - 1))


"""command: download
        self-defined functions can be called by arguments after 'download' command
"""
def download_audio(soup):
    #mms = soup.select("div.hbkDescriptonContents embed")[-1]["src"]
    print("Download not supported, please use the link below in Xunlei or some other download tools.")
    #print(mms_extract(mms))


def download_images(bangumi):
    images = [part[u"pc_image_url"] for part in bangumi[u"episode"][u"episode_parts"] if part[u"pc_image_url"]]

    if images:
        import urllib

        for image in images:
            print("image found")
            print(image)

            print("Downloading"),
            try:
                urllib.urlretrieve(image, filename=get_file_name(image))
                print(" >> Done")
            except Exception, e:
                handle_error(e, " >> Failed")

            print("-"*15)
    else:
        print("No image found.")


"""command: show
        self-defined functions can be called by arguments after 'show' command
"""
def _show_printer(title):
    def decorator(fn):
        @wraps(fn)
        def warpper(*args, **kwds):
            print("-" * 15 + title + "-" * 15)

            string = fn(*args, **kwds)
            if string:
                print("{0}\n".format(string.strip().encode(__codes)))
        return warpper
    return decorator


@_show_printer("Name")
def show_name(bangumi):
    return bangumi[u"name"]


@_show_printer("Description")
def show_description(bangumi):
    return bangumi[u"description"]


@_show_printer("Title")
def show_title(bangumi):
    return bangumi[u"episode"][u"name"]


@_show_printer("Comment")
def show_comment(bangumi):
    return "\n".join([part[u"description"] for part in bangumi[u"episode"][u"episode_parts"]])


@_show_printer("Schedule")
def show_schedule(bangumi):
    return bangumi[u"onair_information"]


@_show_printer("Personality")
def show_personality(bangumi):
    return bangumi[u"cast"].replace(", ", "\n")


@_show_printer("Guest")
def show_guest(bangumi):
    pass


def process(option):

    global __debug
    __debug = option.debug

    if option.sp_name == "list":
        # acquire html content
        try:
            request = urllib2.Request(u"https://vcms-api.hibiki-radio.jp/api/v1/programs", headers=request_headers)
            raw_data = urllib2.urlopen(request, timeout=60).read()
        except Exception, e:
            handle_error(e, "Network Error.")
            return

        bangumis = json.loads(raw_data)

        # handle arguments, fill the IF block
        if option.today:
            # self-definded function for listing out today's bangumi
            list_daily(0, bangumis)

        elif option.day:
            # self-definded function for listing out bangumi of specific day
            list_daily(option.day, bangumis)

        elif option.new:
            # self-definded function for listing out recent new bangumi
            list_new(bangumis)

        elif option.all:
            # self-definded function for listing out all bangumi
            list_all(bangumis)

    elif option.sp_name == "download":
        # acquire html content
        try:
            request = urllib2.Request(u"https://vcms-api.hibiki-radio.jp/api/v1/programs/{id}".format(id=option.id), headers=request_headers)
            raw_data = urllib2.urlopen(request, timeout=60).read()
        except Exception, e:
            handle_error(e, "Network Error.")
            return

        bangumi = json.loads(raw_data)

        # handle arguments, fill the IF block
        if option.everything or option.image:
            # self-defined function for downloading bangumi image
            download_images(bangumi)

        if option.everything or option.audio:
            # self-defined function for downloading bangumi image
            download_audio(bangumi)

    elif option.sp_name == "show":
        # acquire html content
        try:
            request = urllib2.Request(u"https://vcms-api.hibiki-radio.jp/api/v1/programs/{id}".format(id=option.id), headers=request_headers)
            raw_data = urllib2.urlopen(request, timeout=60).read()
        except Exception, e:
            handle_error(e, "Network Error.")
            return

        bangumi = json.loads(raw_data)

        # handle arguments, fill the IF block
        if option.name or option.verbose:
            # self-defined function for showing bangumi name
            show_name(bangumi)

        if option.description or option.verbose:
            # self-defined function for showing bangumi description
            show_description(bangumi)

        if option.title or option.verbose:
            # self-defined function for showing bangumi title
            show_title(bangumi)

        if option.comment or option.verbose:
            # self-defined function for showing bangumi comment
            show_comment(bangumi)

        if option.schedule or option.verbose:
            # self-defined function for showing bangumi schedule
            show_schedule(bangumi)

        if option.personality or option.verbose:
            # self-defined function for showing bangumi personality
            show_personality(bangumi)

        if option.guest or option.verbose:
            # self-defined function for showing bangumi guest
            show_guest(bangumi)


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
    #   -e, --everything: download audio and image
    #   id: bangumi id, usually not the real name of the bangumi but a string
    sp_download = sp.add_parser("download", help="download bangumi")
    sp_download.add_argument("-a", "--audio", action="store_true", dest="audio", help="including audio")
    sp_download.add_argument("-i", "--image", action="store_true", dest="image", help="including image")
    sp_download.add_argument("-e", "--everything", action="store_true", dest="everything", help="including everything")
    sp_download.add_argument("id", action="store", default=None, help="bangumi id")

    # command 'show'
    #
    # Args:
    #   -n, --name: bangumi name
    #   -t, --title: episode title
    #   -c, --comment: comment that will be updated each episode
    #   -d, --description: description of the bangumi
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
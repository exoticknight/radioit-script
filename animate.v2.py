#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import sys
import argparse

from functools import wraps
from bs4 import BeautifulSoup

__debug = False


"""utils
"""
def handle_error(e, message):
    print(message)

    global __debug
    if __debug:
        print("-" * 15)
        print(e)


def get_file_name(url):
    return url.split("/")[-1]


def mms_extract(url):
    soup = BeautifulSoup(urllib2.urlopen(url))
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
def list_all(soup):
    import re
    content = []
    for day in soup.find_all(id=re.compile("mon|tue|wed|thu|fri")):
        content += day.select(".title a")

    # prepare report text
    table = [(u"ID", u"Name")] + [(a["href"][22:], a.get_text()) for a in content]
    # prettify table
    text = prettify_table(table)

    print(text.encode("gb18030"))
    print("\n{0} bangumi counted.".format(len(table) - 1))


def list_daily(soup, day):
    from datetime import date
    day_selector = {
        0: 'mon',
        1: 'tue',
        2: 'wed',
        3: 'thu',
        4: 'fri',
        5: None,
        6: None
    }.get(date.weekday(date.today()) if not day else day[0] - 1, None) # 0 stands for monday in time module

    if not day_selector:
        print("Nothing found.")
        return

    content = soup.select("#{} .contents_block_A .textArea".format(day_selector))

    # prepare report text
    table = [(u"Status", u"ID", u"Name")]

    for p in content:
        status = u"Update" if p.find("span", class_="new") else u"Normal"
        a = p.select(".title a")[0]
        table.append((status, a["href"][22:], a.get_text()))

    # prettify table
    text = prettify_table(table)

    print(text.encode("gb18030"))
    print("\n{0} bangumi counted.".format(len(table) - 1))


def list_new(soup):
    content = soup.select("#newWrap .title a")

    # prepare report text
    table = [(u"ID", u"Name")] + [(a["href"][22:], a.get_text()) for a in content]

    # prettify table
    text = prettify_table(table)

    print(text.encode("gb18030"))
    print("\n{0} bangumi counted.".format(len(table) - 1))


"""command: download
        self-defined functions can be called by arguments after 'download' command
"""
def download_audio(soup):
    mms = (u"http://www.animate.tv{}".format(soup.select(".playBox")[1].select(".btn > a")[0]["href"]))
    print("Download not supported, please use the link below in Xunlei or some other download tools.")
    print(mms_extract(mms))


def download_images(soup):
    images = soup.select(".thumbnail img")

    if images:
        import urllib

        for image in images:
            print("Downloading image: {0}".format(image["src"])),

            try:
                urllib.urlretrieve(image["src"], filename=get_file_name(image["src"]))
                print(" >> Done")
            except Exception, e:
                handle_error(e, " >> Failed")

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
                print("{0}\n".format(string.strip().encode("gb18030")))
        return warpper
    return decorator


@_show_printer("Name")
def show_name(soup):
    content = soup.find(class_="ttl")

    if content:
        return content.get_text()


@_show_printer("Description")
def show_description(soup):
    content = soup.find(id="tab-outline")

    if content:
        return "\n".join(line for line in content.stripped_strings)


@_show_printer("Title")
def show_title(soup):
    content = soup.find(class_="broadcast_title")

    if content:
        return content.get_text()


@_show_printer("Comment")
def show_comment(soup):
    content = soup.find(class_="textBox")

    if content:
        return "\n".join(line for line in content.stripped_strings)


@_show_printer("Schedule")
def show_schedule(soup):
    content = soup.select(".ttlArea .date")

    if content:
        return content[0].get_text()


@_show_printer("Personality")
def show_personality(soup):
    content = soup.find_all(class_="htmlbox_3")

    if content:
        return content[-2].get_text()


@_show_printer("Guest")
def show_guest(soup):
    pass


def process(option):

    global __debug
    __debug = option.debug

    if option.sp_name == "list":
        # write your handle for command 'list' below
        try:
            soup = BeautifulSoup(urllib2.urlopen(u"http://animate.tv/radio/", timeout=60))
        except Exception, e:
            handle_error(e, "Network Error.")
            return

        # handle arguments, fill the IF block
        if option.today:
            # self-definded function for listing out today's bangumi
            list_daily(soup, 0)

        elif option.day:
            # self-definded function for listing out bangumi of specific day
            list_daily(soup, option.day)

        elif option.new:
            # self-definded function for listing out recent new bangumi
            list_new(soup)

        elif option.all:
            # self-definded function for listing out all bangumi
            list_all(soup)

    elif option.sp_name == "download":
        try:
            soup = BeautifulSoup(urllib2.urlopen(u"http://www.animate.tv/radio/{id}/".format(id=option.id), timeout=60))
        except Exception, e:
            handle_error(e, "Network Error.")
            return

        # handle arguments, fill the IF block
        if option.everything or option.image:
            # self-defined function for downloading bangumi image
            download_images(soup)

        if option.everything or option.audio:
            # self-defined function for downloading bangumi image
            download_audio(soup)

    elif option.sp_name == "show":
        try:
            soup = BeautifulSoup(urllib2.urlopen(u"http://www.animate.tv/radio/{id}/".format(id=option.id), timeout=60))
        except Exception, e:
            handle_error(e, "Network Error.")
            return

        # handle arguments, fill the IF block
        if option.name or option.verbose:
            # self-defined function for showing bangumi name
            show_name(soup)

        if option.description or option.verbose:
            # self-defined function for showing bangumi description
            show_description(soup)

        if option.title or option.verbose:
            # self-defined function for showing bangumi title
            show_title(soup)

        if option.comment or option.verbose:
            # self-defined function for showing bangumi comment
            show_comment(soup)

        if option.schedule or option.verbose:
            # self-defined function for showing bangumi schedule
            show_schedule(soup)

        if option.personality or option.verbose:
            # self-defined function for showing bangumi personality
            show_personality(soup)

        if option.guest or option.verbose:
            # self-defined function for showing bangumi guest
            show_guest(soup)


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
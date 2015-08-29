#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import sys
import argparse
import urlparse

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
def list_all():
    # acquire html content
    try:
        soup = BeautifulSoup(urllib2.urlopen(u"http://hibiki-radio.jp/mokuji", timeout=60), "html.parser")
    except Exception, e:
        handle_error(e, "Network Error.")
        return

    content = soup.select(".hbkMokujiTable > table tr:nth-of-type(3) td:nth-of-type(2)")[0]\
                    .select("a[href^=\"http://hibiki-radio.jp/description/\"]")

    # prepare report text
    table = [(u"ID", u"Name")] + [(a["href"][35:], a.get_text()) for a in content]
    # prettify table
    text = prettify_table(table)

    print(text.encode("gb18030"))
    print("\n{0} bangumi counted.".format(len(table) - 1))


def list_daily(day):
    # acquire html content
    try:
        soup = BeautifulSoup(urllib2.urlopen(u"http://hibiki-radio.jp/program", timeout=60), "html.parser")
    except Exception, e:
        handle_error(e, "Network Error.")
        return

    content = soup.select(".hbkProgramTable")

    # polyfill
    content = content + [None] * (7 - len(content))

    from datetime import date
    content = content[date.weekday(date.today()) \
                if not day else day[0] - 1] # 0 stands for monday in time module

    if not content:
        print("Nothing found.")
        return

    # prepare report text
    table = [(u"Status", u"ID", u"Name")]

    table += [(u"Update", p.parent["href"][35:], p.get_text()) \
            for p in content.select(".hbkProgramTitleNew")]
    table += [(u"Normal", p.parent["href"][35:], p.get_text()) \
            for p in content.select(".hbkProgramTitle")]

    # prettify table
    text = prettify_table(table)

    print(text.encode("gb18030"))
    print("\n{0} bangumi counted.".format(len(table) - 1))


def list_new():
    try:
        soup = BeautifulSoup(urllib2.urlopen(u"http://hibiki-radio.jp/mokuji", timeout=60), "html.parser")
    except Exception, e:
        handle_error(e, "Network Error.")
        return

    content = soup.select("li.icon2 a")

    # prepare report text
    table = [(u"ID", u"Name")] + [(a["href"][35:], a.get_text()) for a in content]

    # prettify table
    text = prettify_table(table)

    print(text.encode("gb18030"))
    print("\n{0} bangumi counted.".format(len(table) - 1))


"""command: download
        self-defined functions can be called by arguments after 'download' command
"""
def download_audio(soup):
    mms = soup.select("div.hbkDescriptonContents embed")[-1]["src"]
    print("Download not supported, please use the link below in Xunlei or some other download tools.")
    print(mms_extract(mms))


def download_images(soup):
    images = soup.select("table.hbkTextTable td:nth-of-type(1) div:nth-of-type(3) table:nth-of-type(2) td img")

    if images:
        import urllib

        for image in images:
            print("image found")
            if "click" in image.attrs:
                print("click => {0}".format(image["click"]))
            if "onmouseover" in image.attrs:
                print("onmouseover => {0}".format(image["onmouseover"]))
            print("src => {0}".format(image["src"]))

            try:
                urllib.urlretrieve(image["src"], filename=get_file_name(image["src"]))
                print(">> Done")
            except Exception, e:
                handle_error(e, ">> Failed")
            
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
                print("{0}\n".format(string.strip().encode("gb18030")))
        return warpper
    return decorator


@_show_printer("Name")
def show_name(soup):
    content = soup.find("title")

    if content:
        return content.string[27:-5]


@_show_printer("Description")
def show_description(soup):
    content = soup.select("table.hbkTextTable td:nth-of-type(1) div:nth-of-type(1)")

    if content:
        return content[0].get_text()


@_show_printer("Title")
def show_title(soup):
    content = soup.select("table.hbkTextTable td:nth-of-type(1) div:nth-of-type(3) table:nth-of-type(1) div")

    if content:
        return content[0].string


@_show_printer("Comment")
def show_comment(soup):
    content = soup.select("table.hbkTextTable td:nth-of-type(1) div:nth-of-type(3) table:nth-of-type(2) td")

    if content:
        return content[0].get_text().strip()


@_show_printer("Schedule")
def show_schedule(soup):
    content1 = soup.select("table.hbkTextTable > tr > td:nth-of-type(2) > div")
    content2 = soup.select(".hbkDescriptonContents")[-1].previous_sibling.previous_sibling.previous_sibling.previous_sibling.select("span")[0]
    schedule = ""

    if content1:
        schedule = content1[-5].get_text()
        schedule = content1[-3].get_text() if schedule == "" else schedule

    if content2:
        schedule = schedule + "\n" + content2.string

    return schedule


@_show_printer("Personality")
def show_personality(soup):
    content = soup.select("table.hbkTextTable td:nth-of-type(1) > table table")
    content = [x.select("td")[1].get_text() for x in content]

    if content:
        return "\n".join(content)


@_show_printer("Guest")
def show_guest(soup):
    pass


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
            # self-definded function for listing out recent new bangumi
            list_new()

        elif option.all:
            # self-definded function for listing out all bangumi
            list_all()

    elif option.sp_name == "download":
        # write your handle for command 'download' below
        try:
            soup = BeautifulSoup(urllib2.urlopen(u"http://hibiki-radio.jp/description/{id}".format(id=option.id), timeout=30), "html.parser")
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
        # write your handle for command 'show' below
        try:
            soup = BeautifulSoup(urllib2.urlopen(u"http://hibiki-radio.jp/description/{id}".format(id=option.id), timeout=30), "html.parser")
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

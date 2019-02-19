#!/usr/bin/python3
import os
from datetime import timedelta, datetime
from shutil import rmtree

tmpdir = os.path.expanduser("~/volatile-tmp")

now = datetime.now()
protected_files = ["readme.org", ".volatile"]


def remove(p):
    """Remove file/dir by path"""
    print("removing", p)
    try:
        os.remove(p)
    except IsADirectoryError:
        rmtree(p)


def get_expiry(dir):
    "read .volatile in dir into timedelta"
    with open(dir + "/.volatile", "r") as f:
        line = ""
        while line == "":
            line = f.readline().lstrip().rstrip()

    d = {"weeks": 0, "days": 0, "hours": 0, "minutes": 0, "seconds": 0}

    for i in line.split(','):
        components = i.split("=")
        try:
            d[components[0]] = float(components[1])
        except:
            pass
    return (now - timedelta(
        weeks=d['weeks'],
        days=d['days'],
        hours=d['hours'],
        minutes=d['minutes'],
        seconds=d['seconds']))


expiry = get_expiry(tmpdir)

# scan
things = os.scandir(tmpdir)
for entry in things:

    if not entry.is_dir():  # files first
        if entry.name in protected_files:
            continue
        if datetime.utcfromtimestamp(entry.stat().st_mtime) < expiry:
            remove(entry.path)

    else:
        if os.path.isfile(entry.path + "/" + ".preserve"):
            continue
        try:
            dir_expiry = get_expiry(entry.path)
        except FileNotFoundError:
            dir_expiry = expiry
        # get newest file in subdir tree
        all_files = []
        for root, dirs, files in os.walk(entry.path):
            for f in files:
                all_files.append(root + "/" + f)
        if len(all_files) == 0:  # cleanup empty dirs
            remove(entry.path)
        elif datetime.utcfromtimestamp(
                os.path.getmtime(max(all_files,
                                     key=os.path.getmtime))) < dir_expiry:
            remove(entry.path)

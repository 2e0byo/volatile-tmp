#!/usr/bin/python3
import os
from datetime import datetime, timedelta
from shutil import rmtree
import logging

logger = logging.getLogger(__name__)

tmpdir = os.path.expanduser("~/volatile-tmp")

now = datetime.now()
protected_files = ("readme.org", ".volatile")


def remove(p):
    """Remove file/dir by path."""
    print("removing", p)
    try:
        os.remove(p)
    except IsADirectoryError:
        rmtree(p)


def get_expiry(directory):
    """read .volatile in dir into timedelta."""
    with open(directory + "/.volatile", "r") as f:
        line = ""
        while line == "":
            line = f.readline().lstrip().rstrip()

    d = {"weeks": 0, "days": 0, "hours": 0, "minutes": 0, "seconds": 0}

    for i in line.split(","):
        components = i.split("=")
        try:
            d[components[0]] = float(components[1])
        except:
            pass
    return now - timedelta(
        weeks=d["weeks"],
        days=d["days"],
        hours=d["hours"],
        minutes=d["minutes"],
        seconds=d["seconds"],
    )


expiry = get_expiry(tmpdir)

# scan
things = os.scandir(tmpdir)
for entry in things:
    try:

        if not entry.is_dir():  # files first
            if entry.name in protected_files:
                continue
            if os.path.islink(entry.path) and not os.path.exists(entry.path):
                remove(entry.path)
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
                    f = root + "/" + f
                    if os.path.islink(f) and not os.path.exists(f):
                        logger.info("Removing dead symlink")
                        remove(f)
                    else:
                        all_files.append(f)
            if len(all_files) == 0:  # cleanup empty dirs
                logger.info("Removing empty dir " + entry.path)
                remove(entry.path)
            elif (
                datetime.utcfromtimestamp(max(os.path.getmtime(f) for f in all_files))
                < dir_expiry
            ):
                remove(entry.path)

    except Exception as e:
        logger.exception(e)

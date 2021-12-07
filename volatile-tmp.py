#!/usr/bin/python3
import os
from datetime import datetime, timedelta
from shutil import rmtree
import logging
from time import perf_counter

logger = logging.getLogger(__name__)

volatiledir = os.path.expanduser("~/volatile-tmp")

now = datetime.now()
protected_files = ("readme.org", ".volatile")


def remove(p: str, reason: str = None):
    """Remove file/dir by path."""
    logger.info(f"Removing {p}" + f" Reason: {reason}" if reason else "")
    try:
        os.remove(p)
    except IsADirectoryError:
        rmtree(p)


def get_expiry(directory: str):
    """read .volatile in dir into timedelta."""
    with open(directory + "/.volatile", "r") as f:
        line = ""
        while line == "":
            line = f.readline().lstrip().rstrip()
def cleanup_symlink(fn: str):
    """Delete dangling symlinks."""
    if os.path.islink(fn) and not os.path.exists(fn):
        remove(path, "Dangling symlink.")
        return True

    return False


def process_file(fn: str, path: str, expiry: datetime):
    """Process an individual file"""
    if fn in protected_files:
        logger.debug(f"Skipping Protected file {fn}.")
        return False

    if cleanup_symlink(fn):
        return True

    if datetime.utcfromtimestamp(entry.stat().st_mtime) < expiry:
        remove(entry.path, "File expired.")
        return True

    return False


if __name__ == "__main__":

    expiry = get_expiry(volatiledir)

    # scan
    for entry in os.scandir(volatiledir):
        logger.debug(f"Considering {entry}")
        try:

            if not entry.is_dir():  # files first
                process_file(entry.name, entry.path, expiry)

            else:
                if os.path.isfile(entry.path + "/" + ".preserve"):
                    logger.debug(".preserve exists, skipping.")
                    continue
                try:
                    dir_expiry = get_expiry(entry.path)
                except FileNotFoundError:
                    dir_expiry = expiry

                # get newest file in subdir tree
                logger.debug("Getting all files")
                start = perf_counter()
                newest = ()

                all_files = []
                total = 0
                for root, dirs, files in os.walk(entry.path):
                    for fn in files:
                        total += 1
                        fn = root + "/" + fn
                        if not cleanup_symlink(fn):
                            newest = max(newest, (os.path.getmtime(fn), fn))

                logger.debug(f"Scanned {total} files in {perf_counter() - start :>.3}s")

                if not newest:
                    remove(entry.path, "Empty dir.")
                else:
                    modt, fn = newest
                    modt = datetime.utcfromtimestamp(modt)
                    if modt < dir_expiry:
                        remove(
                            entry.path,
                            f"Newest file {fn} in dir expired: last modified {modt}.",
                        )

        except Exception as e:
            logger.exception(e)

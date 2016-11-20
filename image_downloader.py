#!/usr/bin/env python3
import itertools
import logging
import sys
from os.path import basename, splitext, isfile
from urllib.parse import urlsplit

import requests


def get_logger():
    logger = logging.getLogger(__name__)
    formatter = logging.Formatter("[%(asctime)s %(name)s:%(lineno)d %(levelname)s] %(message)s")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger


logger = get_logger()


def get_urls_from_file(filename):
    with open(filename, 'r') as f:
        return f.readlines()


class DownloadError(Exception):
    pass


class ImageDownloader(object):
    @classmethod
    def download(cls, urls):
        for url in urls:
            try:
                logger.debug('Downloading image from url: %s' % url)
                filename, data = cls.get_image(url)
                cls.save(filename, data)
            except DownloadError:
                pass

    @staticmethod
    def get_image(url):
        response = requests.get(url)
        if not response.status_code == 200:
            logger.warn("Can't download url %s, response code %s" % (url, response.status_code))
            raise DownloadError()

        filename = basename(urlsplit(url)[2])
        return filename, response.content

    @classmethod
    def save(cls, filename, data):

        for filename in cls.increment_filename_suffix(filename):
            if not isfile(filename):
                break

        with open(filename, 'wb') as f:
            f.write(data)

        logger.debug('Saved %s' % filename)

    @staticmethod
    def increment_filename_suffix(filename):
        yield filename
        name, ext = splitext(filename)
        for n in itertools.count(start=1):
            yield '%s-%d%s' % (name, n, ext)


if __name__ == '__main__':
    urls = get_urls_from_file(sys.argv[1])
    ImageDownloader.download(urls)

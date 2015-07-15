#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Image content gap module."""

import logging

import requests

import contentgap
import report

# Constants
LOGGER_NAME = 'sicglog'
WIKIPEDIA_URL = '{0}.wikipedia.org'
PROTOCOL = 'https'
USER_AGENT = 'Bot based on mwclient'
GROK_SE_URL = "http://stats.grok.se/json/{0:s}/latest{1:d}/{2:s}"
GROK_MISSING_DAILY_VIEWS = "grok.se invalid result, missing daily_views"
MAX_TIME_WITHOUT_UPDATE = 600

ARTICLE_NAMESPACE = 0
CATEGORY_NAMEPSACE = 14

# logger
LOG = logging.getLogger(LOGGER_NAME)


class MissingDailyViewsException(ValueError):

    """When dail_views is not in the grok response."""
    pass


def isthereanimage(article):
    """Returns whether there is an image in the article or not."""
    LOG.info("Analyzing: %s", article.name.encode('utf-8'))
    imagepattern = ["<gallery>", "File:", "Image:", ".jpg", ".JPG", ".gif",
                    ".GIF", ".PNG", ".SVG", ".TIF",
                    ".png", ".svg", ".tif", ".jpeg", ".JPEG"]
    text = article.text()
    return any(pattern in text for pattern in imagepattern)


def latest90(article):
    """Returns amount of views from the latest 90 days

    Args:
        article (article): article on which we are querying stats.

    Returns:
        int: sum of daily views.

    Raises:
        MissingDailyViewsException: if daily_views are missing from response.
    """
    url = GROK_SE_URL.format(article.site.site['lang'],
                             90,
                             article.name.encode('utf-8'))
    LOG.debug('\tRequest to %s', url)
    result = requests.get(url).json()
    if 'daily_views' in result:
        return sum([result['daily_views'][d] for d in result['daily_views']])
    else:
        raise MissingDailyViewsException(GROK_MISSING_DAILY_VIEWS)


class Callback(object):

    """Callback for image content gap."""

    def __init__(self, timer, site, reportname):
        """Constructor.

        Args:
            timer (int): timer in seconds
            site (mwclient.Site): wikipedia site object the script is running
                on
        """
        self.timer = timer
        self.site = site
        self.reportname = reportname

    def callback(self):
        """Return the callback as dictionnary."""
        def callback_function(gap):
            content = report.create(gap.ranked_articles)  # report content
            report.save(self.site, self.reportname, content)
        return {'timer': self.timer, 'function': callback_function}


def setuplog():
    """Set up the LOG. """
    consolehandler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s    %(levelname)s    %(message)s')
    consolehandler.setFormatter(formatter)
    consolehandler.setLevel(logging.INFO)
    LOG.addHandler(consolehandler)
    logfilehandler = logging.FileHandler('sicg.log')
    logfilehandler.setFormatter(formatter)
    logfilehandler.setLevel(logging.DEBUG)
    LOG.addHandler(logfilehandler)
    LOG.setLevel(logging.DEBUG)


def main():
    """Main script of the image content gap"""
    setuplog()
    articles = []  # dummy code
    callback = Callback(600, None, None)
    gap = contentgap.ContentGap(articles)
    gap.filterandrank([isthereanimage],
                      latest90,
                      callback)

if __name__ == '__main__':
    main()

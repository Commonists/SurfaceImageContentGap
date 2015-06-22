#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Surface image content gap."""

from ConfigParser import RawConfigParser
import logging
import time

import mwclient
import requests

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
    """ Returns whether there is an image in the article or not."""
    LOG.info("Analyzing: %s", article.name.encode('utf-8'))
    imagepattern = ["<gallery>", "File:", "Image:", ".jpg", ".JPG", ".gif",
                    ".GIF", ".PNG", ".SVG", ".TIF",
                    ".png", ".svg", ".tif", ".jpeg", ".JPEG"]
    text = article.text()
    return any(pattern in text for pattern in imagepattern)


def getlatest(article, latest):
    """ Returns amount of views from the latest days

    Args:
        article (article): article on which we are querying stats.
        latest (int): amount of days we are going to fetch
            values must be 30, 60, or 90

    Returns:
        int: sum of daily views.

    Raises:
        ValueError: if latest is not in [30, 60, 90]
        MissingDailyViewsException: if daily_views are missing from response.
    """
    if latest not in [30, 60, 90]:
        raise ValueError("Expected 30, 60 or 90 instead of %s" % (latest))
    url = GROK_SE_URL.format(article.site.site['lang'],
                             latest,
                             article.name.encode('utf-8'))
    LOG.debug('\tRequest to %s', url)
    result = requests.get(url).json()
    if 'daily_views' in result:
        return sum([result['daily_views'][d] for d in result['daily_views']])
    else:
        raise MissingDailyViewsException(GROK_MISSING_DAILY_VIEWS)


def sortandwritereport(site, reportname, result):
    """Sort results and write it to a report. Returns the sorted result.

    Args:
        site (mwclient.Site): wikipedia site
        reportname (str): page to save the report to.
        result (list): list of articles with their last 90 days views.
    """
    sorted_result = sorted(result, key=lambda x: -x['views'])
    reportcontent = report.create(sorted_result)
    report.save(site, reportname, reportcontent)
    LOG.info("Save report to %s", reportname)
    return sorted_result


def searcharticles(category, depth=0):
    """Search articles in category and its subcategories
    until a given depth.

    Args:
        category (mwclient.Category): category to search
        depth (int): how deep should we search (0 means only the category,
            1 the category and it's sub categories, etc.
    """
    allcontent = [a for a in category]
    articles = [a for a in allcontent if a.namespace == ARTICLE_NAMESPACE]
    categories = [c for c in allcontent if c.namespace == CATEGORY_NAMEPSACE]
    LOG.info("Searching for articles into %s", category.name.encode('utf-8'))
    if depth > 0 and len(categories) > 0:
        for subcat in categories:
            articles += searcharticles(subcat, depth - 1)
    return articles


def crawlcategory(category, site, reportname, depth=0):
    """Crawl the category from a given wikipedia.

    Args:
        category (str): name of the category to crawl.
        site (mwclient.Site): site object.
        reportname (str): name of the report page.
        depth (int): max recursivity depth

    Returns
        list: containing dictionnaries with the article name and the total view
    """
    last_update = time.time()  # init to time.time()
    category = site.Categories[category.decode('utf-8')]
    articles = searcharticles(category, depth=depth)
    noimagearticles = []
    LOG.info("Found: %s articles", len(articles))
    for article in articles:
        if not isthereanimage(article):
            LOG.info("\tNo image found in: %s", article.name.encode('utf-8'))
            noimagearticles.append({'name': article.name.encode('utf-8'),
                                    'views': getlatest(article, 90)})
            if time.time() - last_update > MAX_TIME_WITHOUT_UPDATE:
                sortandwritereport(site, reportname, noimagearticles)
                last_update = time.time()
    LOG.info("Finished, found %s articles without images out of %s",
             len(noimagearticles),
             len(articles))
    return sortandwritereport(site, reportname, noimagearticles)


def readconfig(configname):
    """Read the config file.

    Args:
        configname (str): configuration file name. Should have section login
            and entry for user and password.

    Returns:
        dict: with user and password key.

    Raises:
        ValueError: when configname is None
    """
    if configname is None:
        raise ValueError('Config file should be provided with -f/--configfile')
    configparser = RawConfigParser()
    configparser.read(configname)
    return {'user': configparser.get('login', 'user'),
            'password': configparser.get('login', 'password')}


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
    """main function."""
    setuplog()
    from argparse import ArgumentParser
    description = 'Analyzing Wikipedia to surface image content gap.'
    parser = ArgumentParser(description=description)
    parser.add_argument('-c', '--category',
                        type=str,
                        dest='category',
                        required=False,
                        default='Portail:Informatique théorique/Articles liés',
                        help='Article category on wikipedia')
    parser.add_argument('-w', '--wikipedia',
                        type=str,
                        dest='lang',
                        required=True,
                        help='Language code for Wikipedia')
    parser.add_argument('-r', '--report',
                        type=str,
                        dest='report',
                        required=True,
                        help='Page name to write a report.')
    parser.add_argument('-f', '--configfile',
                        type=str,
                        dest='config',
                        required=True,
                        help='Config file with login and password.')
    parser.add_argument('-d', '--depth',
                        type=int,
                        dest='depth',
                        required=False,
                        default=0,
                        help='Depth of search into a category.')
    args = parser.parse_args()
    site = mwclient.Site((PROTOCOL, WIKIPEDIA_URL.format(args.lang)),
                         clients_useragent=USER_AGENT)
    conf = readconfig(args.config)
    site.login(conf['user'], conf['password'])
    crawlcategory(args.category, site, args.report)


if __name__ == '__main__':
    main()

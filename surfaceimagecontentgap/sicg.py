#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Surface image content gap."""

from ConfigParser import RawConfigParser
import logging

import mwclient
import requests

import report


# logger
LOG = logging.getLogger()

# Constants
WIKIPEDIA_URL = '{0}.wikipedia.org'
PROTOCOL = 'https'
USER_AGENT = 'Bot based on mwclient'
GROK_SE_URL = "http://stats.grok.se/json/{0:s}/latest{1:d}/{2:s}"


def isthereanimage(article):
    """ Returns whether there is an image in the article or not."""
    LOG.info("Analyzing: %s", article.name.encode('utf-8'))
    imagepattern = ["<gallery>", "File:", "Image:", ".jpg", ".JPG", ".gif",
                    ".GIF", ".PNG", ".SVG", ".TIF",
                    ".png", ".svg", ".tif"]
    text = article.text()
    result = any(pattern in text for pattern in imagepattern)
    return result


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
        raise ValueError("grok.se invalid result, missing daily_views")


def crawlcategory(language, category):
    """Crawl the category from a given wikipedia.

    Args:
        language (str): language code of wikipedia
        category (str): name of the category to crawl.

    Returns
        list: containing dictionnaries with the article name and the total view
    """
    site = mwclient.Site((PROTOCOL, WIKIPEDIA_URL.format(language)),
                         clients_useragent=USER_AGENT)
    articles = [a for a in site.Categories[category.decode('utf-8')]]
    noimagearticles = []
    LOG.info("Found: %s articles", len(articles))
    for article in articles:
        if not isthereanimage(article):
            noimagearticles.append({'name': article.name.encode('utf-8'),
                                    'views': getlatest(article, 90)})
            LOG.info("\tNo image found in: %s", article.name.encode('utf-8'))
    LOG.info("Finished, found %s articles without images out of %s",
             len(noimagearticles),
             len(articles))
    sorted_result = sorted(noimagearticles,
                           key=lambda x: -x['views'])
    return sorted_result


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
                        required=False,
                        default=None,
                        help='Optional, page name to write a report.')
    parser.add_argument('-f', '--configfile',
                        type=str,
                        dest='config',
                        required=False,
                        default=None,
                        help='Optional, config file with login and password.')
    args = parser.parse_args()
    result = crawlcategory(args.lang, args.category)
    if args.report is not None:
        conf = readconfig(args.config)
        site = mwclient.Site((PROTOCOL, WIKIPEDIA_URL.format(args.lang)),
                             clients_useragent=USER_AGENT)
        site.login(conf['user'], conf['password'])
        myreport = report.create(result)
        report.save(site, args.report, myreport)

if __name__ == '__main__':
    main()

#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Surface image content gap."""

import logging

import mwclient
import requests


# logger
LOG = logging.getLogger()

# Constants
WIKIPEDIA_URL = '{0}.wikipedia.org'
PROTOCOL = 'https'
USER_AGENT = 'Bot based on mwclient'
GROK_SE_URL = "http://stats.grok.se/json/{0:s}/getlatest{1:d}/{2:s}"


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
    """ Returns amount of views from the getlatest days

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
    """
    site = mwclient.Site((PROTOCOL, WIKIPEDIA_URL.format(language)),
                         clients_useragent=USER_AGENT)
    articles = [a for a in site.Categories[category.decode('utf-8')]]
    noimagearticles = []
    LOG.info("Found: %s articles", len(articles))
    for article in articles:
        if not isthereanimage(article):
            noimagearticles.append((article, getlatest(article, 90)))
            LOG.info("\tNo image found in: %s", article.name.encode('utf-8'))
    LOG.info("Finished, found %s articles without images out of %s",
             len(noimagearticles),
             len(articles))
    sorted_result = sorted(noimagearticles,
                           key=lambda x: x[1])
    return sorted_result


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
    """ main script. """
    setuplog()
    from argparse import ArgumentParser
    description = 'Analyzing Wikipedia to surface image content gap.'
    parser = ArgumentParser(description=description)
    parser.add_argument("-c", "--category",
                        type=str,
                        dest="category",
                        required=False,
                        default='Portail:Informatique théorique/Articles liés',
                        help="Article category on wikipedia")
    parser.add_argument("-w", "--wikipedia",
                        type=str,
                        dest="lang",
                        required=True,
                        help="Language code for Wikipedia")
    args = parser.parse_args()
    result = crawlcategory(args.lang, args.category)
    for (article, viewcount) in result:
        print "{0}\t\t{1}".format(article.name, viewcount)


if __name__ == '__main__':
    main()

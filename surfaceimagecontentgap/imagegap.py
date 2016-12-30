#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Image content gap module."""

from ConfigParser import RawConfigParser
import logging

import mwclient

import contentgap
import report
import mwtemplate

import pageviewapi.period

# Constants
LOGGER_NAME = 'sicglog'
WIKIPEDIA_URL = '{0}.wikipedia.org'
PROTOCOL = 'https'
USER_AGENT = 'Bot based on mwclient'
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
    """
    project = '{lang}.wikipedia'.format(lang=article.site.site['lang'])
    return pageviewapi.period.sum_last(project,
                                       article.name.encode('utf-8'),
                                       last=90,
                                       access='all-access',
                                       agent='all-agents')


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
            """The call back function to call in order to save result."""
            LOG.info("Saving reports to %s", self.reportname)
            info = gap.metadata()
            content = report.create(gap.ranked_articles,
                                    articles=info['articles'],
                                    filtered_articles=info['filtered'])
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
    from argparse import ArgumentParser
    setuplog()
    description = 'Analyzing Wikipedia to surface image content gap.'
    parser = ArgumentParser(description=description)
    parser.add_argument('-c', '--category',
                        type=str,
                        dest='category',
                        required=False,
                        default=None,
                        help='Article category on wikipedia')
    parser.add_argument('-t', '--template',
                        type=str,
                        dest='template',
                        required=False,
                        default=None,
                        help='Searching for articles including this template')
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
    if args.template is None and args.category is None:
        raise ValueError("Use -t TEMPLATE or -c CATEGORY")
    if args.template is not None and args.category is not None:
        raise ValueError("Use only one of -t/-c")
    site = mwclient.Site((PROTOCOL, WIKIPEDIA_URL.format(args.lang)),
                         clients_useragent=USER_AGENT)
    # login to the site
    configparser = RawConfigParser()
    configparser.read(args.config)
    site.login(configparser.get('login', 'user'),
               configparser.get('login', 'password'))
    # fetch articles list
    articles = []
    LOG.info("Start searching articles")
    if args.category is None:
        search = mwtemplate.ArticleWithTemplate(site, args.template)
        articles = search.listarticles()
    else:
        category = site.Categories[args.category.decode('utf-8')]
        articles = searcharticles(category)
    # get the call back
    callback = Callback(MAX_TIME_WITHOUT_UPDATE, site, args.report)
    gap = contentgap.ContentGap(articles)
    gap.filterandrank([lambda x: not isthereanimage(x)],
                      latest90,
                      callback.callback())


if __name__ == '__main__':
    main()

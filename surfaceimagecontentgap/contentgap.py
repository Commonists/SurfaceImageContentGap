# -*- coding: utf-8 -*-

"""Content Gap Module provides search and ranking for content gap."""

import logging

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


def isthereanimage(article):
    """ Returns whether there is an image in the article or not."""
    LOG.info("Analyzing: %s", article.name.encode('utf-8'))
    imagepattern = ["<gallery>", "File:", "Image:", ".jpg", ".JPG", ".gif",
                    ".GIF", ".PNG", ".SVG", ".TIF",
                    ".png", ".svg", ".tif", ".jpeg", ".JPEG"]
    text = article.text()
    return any(pattern in text for pattern in imagepattern)


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


class ContentGap(object):

    """Find content gap from article list."""

    def __init__(self, site, articles, filters=[], ranking=None):
        """Constructor.

        Args:
            site (mwclient.Site): Wikipedia to search on.
            filters (list): list of filter function to apply to the list of
                articles
            ranking (function): function that associate an article to a ranking
                value. The greater the value, the more important the article
                is.
        """
        pass


class CategoryImageContentGap(ContentGap):

    """Find articles from a category lacking of images"""

    def __init__(self, site, category, depth=0):
        super(CategoryImageContentGap, self).__init__(site,
                                                      searcharticles(category, depth=depth),
                                                      filters=[isthereanimage],
                                                      ranking=lambda x: 42)

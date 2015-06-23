# -*- coding: utf-8 -*-

"""Content Gap Module provides search and ranking for content gap."""

import logging
import requests

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


class ContentGap(object):

    """Find content gap from article list."""

    def __init__(self, site, articles):
        """Constructor.

        Args:
            site (mwclient.Site): Wikipedia to search on.
            filters (list): list of filter function to apply to the list of
                articles
            ranking (function): function that associate an article to a ranking
                value. The greater the value, the more important the article
                is.
        """
        self.site = site
        self.articles = articles
        self.filtered_articles = None
        self.ranked_articles = None

    def filterarticles(self, filters=[]):
        """Filters articles based on filter list.

        The filtered articles list is available as filtered_articles attribute.

        Args:
            filters (list): List of filter function, to apply to the list of
                articles. A filter returns True to keep an articles."""
        self.filtered_articles = self.articles
        for current_filter in filters:
            self.filtered_articles = [x for x in self.filtered_articles
                                      if current_filter(x)]
        return self.articles

    def rankedarticles(self, ranking=None):
        pass

    def reset(self):
        """Reset filter and ranking to None."""
        self.filtered_articles = None
        self.ranked_articles = None

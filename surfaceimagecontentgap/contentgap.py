# -*- coding: utf-8 -*-

"""Content Gap Module provides search and ranking for content gap."""

import logging

# Constants
LOGGER_NAME = 'sicglog'

# logger
LOG = logging.getLogger(LOGGER_NAME)


class ArticlesNotFilteredException(Exception):

    """Exception to raise when articles should have been filtered before
    performing an operation or calling a method."""
    pass


class ContentGap(object):

    """Find content gap from article list."""

    def __init__(self, site, articles):
        """Constructor.

        Args:
            site (mwclient.Site): Wikipedia site to search on.
            articles (list): List of wikipedia articles.

        Attributes:
            site (mwclient.Site): Wikipedia site (i.e. specific language)
            articles (list): List of Wikipedia Articles
            filtered_articles (list): Filtered list of articles, None when not
                filtered.
            ranked_articles (list): List of articles sorted by rank
        """
        self.site = site
        self.articles = articles
        self.filtered_articles = None
        self.ranked_articles = None

    def filterarticles(self, filters=None):
        """Filters articles based on filter list.

        The filtered articles list is available as filtered_articles attribute.

        Args:
            filters (list): List of filter function, to apply to the list of
                articles. A filter returns True to keep an articles."""
        self.filtered_articles = self.articles
        if filters is None:
            filters = []
        for current_filter in filters:
            self.filtered_articles = [x for x in self.filtered_articles
                                      if current_filter(x)]
        return self.articles

    def rankarticles(self, ranking=None):
        """Ranks the articles."""
        if self.filtered_articles is None:
            raise ArticlesNotFilteredException
        if ranking is None:
            self.ranked_articles = [{'article': article, 'rank': 0}
                                    for article in self.filtered_articles]
        else:
            self.ranked_articles = [
                {'article': article, 'rank': ranking(article)}
                for article in self.filtered_articles]
            self.ranked_articles = sorted(self.ranked_articles,
                                          key=lambda x: -x['rank'])
        return self.ranked_articles

    def reset(self):
        """Reset filter and ranking to None."""
        self.filtered_articles = None
        self.ranked_articles = None

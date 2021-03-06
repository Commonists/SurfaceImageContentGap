# -*- coding: utf-8 -*-

"""Content Gap Module provides search and ranking for content gap."""

import logging
import time

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

    def __init__(self, articles):
        """Constructor.

        Args:
            articles (list): List of wikipedia articles.

        Attributes:
            articles (list): List of Wikipedia Articles
            filtered_articles (list): Filtered list of articles, None when not
                filtered.
            ranked_articles (list): List of articles sorted by rank
        """
        self.articles = articles
        self.filtered_articles = None
        self.ranked_articles = None

    def filter(self, filters=None):
        """Filters articles based on filter list.

        The filtered articles list is available as filtered_articles attribute.

        Args:
            filters (list): List of filter function, to apply to the list of
                articles. A filter returns True to keep an articles."""
        self.filtered_articles = []
        if filters is None:
            filters = []
        for article in self.articles:
            if all(keep(article) for keep in filters):
                self.filtered_articles.append(article)
        return self.filtered_articles

    def rank(self, evaluation=None):
        """Ranks the articles according to an evaluation function.

        Args:
            evaluation (function): Function which gives a evaluation of an
                article the higher, the better.
        Returns:
            list: List of {'article': x, 'evaluation': evaluation(x)}
        """
        if self.filtered_articles is None:
            raise ArticlesNotFilteredException
        if evaluation is None:
            self.ranked_articles = [{'article': article.name.encode('utf-8'),
                                     'evaluation': 0}
                                    for article in self.filtered_articles]
        else:
            self.ranked_articles = [
                {'article': article.name.encode('utf-8'),
                 'evaluation': evaluation(article)}
                for article in self.filtered_articles]
            self.ranked_articles = sorted(self.ranked_articles,
                                          key=lambda x: -x['evaluation'])
        return self.ranked_articles

    @staticmethod
    def rankingkey(articledict):
        """Ranking articledict from the greatest 'evaluation' to the lower."""
        return -articledict['evaluation']

    def filterandrank(self, filters, evaluation, callback):
        """Filter and ranks article at the same time, and do an action on a
        callback (such as saving result).

        Args:
            filters (list): List of filter function, to apply to the list of
                articles. A filter returns True to keep an articles.
            evaluation (function): Function which gives a evaluation of an
                article the higher, the better.
            callback (dict): {'timer': t, 'function': c} after duration of
                timer, the callback function is called."""
        last_callback = time.time()
        self.filtered_articles = []
        self.ranked_articles = []
        for article in self.articles:
            if all(keep(article) for keep in filters):
                self.filtered_articles.append(article)
                articlename = article.name.encode('utf-8')
                score = evaluation(article)
                self.ranked_articles.append({'article': articlename,
                                             'evaluation': score})
                if time.time() - last_callback > callback['timer']:
                    self.ranked_articles = sorted(self.ranked_articles,
                                                  key=self.rankingkey)
                    callback['function'](self)
                    last_callback = time.time()
        self.ranked_articles = sorted(self.ranked_articles,
                                      key=self.rankingkey)
        callback['function'](self)

    def reset(self):
        """Reset filter and ranking to None."""
        self.filtered_articles = None
        self.ranked_articles = None

    def metadata(self):
        """Informations about the number of articles and filtered articles."""
        len_articles = 0
        if self.articles:
            len_articles = len(self.articles)
        len_filtered_articles = 0
        if self.filtered_articles:
            len_filtered_articles = len(self.filtered_articles)
        return {'articles': len_articles,
                'filtered': len_filtered_articles}

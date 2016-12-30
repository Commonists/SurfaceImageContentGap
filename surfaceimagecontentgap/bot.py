"""Bot module for SurfaceContentImageGap"""
try:
    from ConfigParser import RawConfigParser
except ImportError:
    from configparser import RawConfigParser

import mwclient

from surfaceimagecontentgap import (
    __version__,
    contentgap,
    logger)
from surfaceimagecontentgap.imagegap import Callback


LOG = logger.logger()
WIKIPEDIA_URL = '{0}.wikipedia.org'
USER_AGENT = 'SurfaceContentGapBot v{0}, using mwclient v{1}'


def user_agent():
    """User agent with version of SurfaceImageContentGap and mwclient version"""
    return USER_AGENT.format(__version__, mwclient.__ver__)


class SurfaceContentGapBot(object):

    """The bot class.

    Attributes:
        site (mwclient.Site): Site object to wikipedia
        config_file (str): Path to the credential configuration file
    """
    def __init__(self, config_file=None, lang='fr', report=None,
                 list_fun=None, filter_fun=None, rank_fun=None,
                 frequency=600):
        """Constructor.

        Args:
            config_file (str, optional): Path to the credential configuration
                file
            lang (str, optional): Language code of the wikipedia.
                Default is 'fr'
            report (str): Page name to write bot report
            list_fun (function):
            filter_fun (function):
            rank_fun (function):
            frequency (int): Amount of seconds between two write of report
        """
        # site
        agent = user_agent()
        self.site = mwclient.Site(WIKIPEDIA_URL.format(lang),
                                  clients_useragent=agent)
        LOG.info("User-Agent: '%s'", agent)

        # Configuration
        self.config_file = config_file
        self.__is_logged__ = False

        # Report page
        self.report = report

        # Listing articles
        self.list_fun = list_fun

        # Filtering articles from list
        self.filter_fun = filter_fun

        # Ranking articles from list
        self.rank_fun = rank_fun

        # Time for report callback
        self.frequency = frequency

    def login(self, config_file=None):
        """Login wikipedia using credential configuration file.

        If config_file argument is filled to the method, it override the one
        of the object (and save it). Other wise it uses the config_file
        attribute.

        Args:
            config_file (str, optional): Path to the credential configuration
                file.

        Raises:
            ValueError: when neither config_file is given to the method or to
                the objects.
        """
        if config_file is not None:
            self.config_file = config_file
        elif self.config_file is None:
            raise ValueError('Trying to login without config_file')
        configparser = RawConfigParser()
        configparser.read(self.config_file)
        self.site.login(configparser.get('login', 'user'),
                        configparser.get('login', 'password'))
        self.__is_logged__ = True
        LOG.info("Logged in as '%s'", configparser.get('login', 'user'))

    def run(self):
        # login if config file but not done
        if not self.__is_logged__ and self.config_file is not None:
            self.login()
        callback = Callback(self.frequency, self.site, self.report)

        # articles list
        articles = self.list_fun(self)

        def filter_article(article):
            return self.filter_fun(self, article)

        def rank(article):
            return self.rank_fun(self, article)
        gap = contentgap.ContentGap(articles)
        gap.filterandrank([filter_article], rank, callback.callback())

#/usr/bin/python
# -*- coding: utf-8 -*-

""" Surface image content gap. """

import logging

import mwclient

LOG = logging.getLogger()
WIKIPEDIA_URL = '{0}.wikipedia.org'
PROTOCOL = 'https'


def isthereanimage(article):
    """ Returns whether there is an image in the article or not. """
    imagepattern = ["<gallery>", "File:", "Image:", ".jpg", ".JPG"]
    text = article.text()
    return any(pattern in text for pattern in imagepattern)


def crawlcategory(language, category):
    """ Crawls the category from a given wikipedia.

    Args:
        language (str): language code of wikipedia
        category (str): name of the category to crawl.
    """
    site = mwclient.Site((PROTOCOL, WIKIPEDIA_URL.format(language)))
    articles = [a for a in site.Categories[category.decode('utf-8')]]
    noimagearticles = []
    for article in articles:
        LOG.debug("Analyzing %s", article.name)
        if not isthereanimage(article):
            noimagearticles.append(article)
    LOG.info("""%s articles, %s article without image""",
             len(articles),
             len(noimagearticles))


def setuplog():
    """ Setting up the LOG. """
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
    crawlcategory(args.lang, args.category)


if __name__ == '__main__':
    main()

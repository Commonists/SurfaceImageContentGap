# -*- coding: utf-8 -*-

"""Reports for image content gap."""


def create(articlelist, articles=None, filtered_articles=None):
    """Create a report from article list with views

    Args:
        articlelist (list): list of dictionnaries with article and evaluation
            for each article [{'article': 'Foo', 'evaluation': 42}, ...]
        articles (optional: int): number of articles to process
        filtered_articles (optional: int): number of articles filtered
    Returns:
        str: wiki code for the report
    """
    reportcode = "== Report ==\n"
    reportcode += """{| class="wikitable"\n|-\n! Article\n! Views\n"""
    for article in articlelist:
        reportcode += "|-\n| [[{0}]]\n| {1}\n".format(article['article'],
                                                      article['evaluation'])
    reportcode += "|}\n"
    if articles and filtered_articles:
        reportcode += "== Data ==\n"
        reportcode += "* total articles: %d\n" % articles
        reportcode += "* filtered articles: %d\n" % filtered_articles
    return reportcode


def save(site, pagename, report):
    """Save report on the wiki site as pagename.

    Args:
        site (mwclient.Site): wiki to save to
        pagename (str): name of the page to save the report to
        report (str): surface image content gap report
    """
    page = site.Pages[pagename.decode('utf-8')]
    page.save(report, summary='Content gap report')

# -*- coding: utf-8 -*-

"""Reports for image content gap."""


def create(articlelist):
    """Create a report from article list with views

    Args:
        articlelist (list): list of dictionnaries with article and evaluation
            for each article [{'article': 'Foo', 'evaluation': 42}, ...]
    Returns:
        str: wiki code for the report
    """
    reportcode = "== Report ==\n"
    reportcode += """{| class="wikitable"\n|-\n! Article\n! Views\n"""
    for article in articlelist:
        reportcode += "|-\n| [[{0}]]\n| {1}\n".format(article['article'],
                                                      article['evaluation'])
    reportcode += "|}\n"
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

# -*- coding: utf-8 -*-

"""Reports for image content gap."""


def create(articlelist):
    """Create a report from article list with views

    Args:
        articlelist (list): list of dictionnaries with name and views for
            each article [{'name': 'Foo', 'views': 42}, ...]
    Returns:
        str: wiki code for the report
    """
    reportcode = "== Report ==\n"
    for article in articlelist:
        reportcode += "* [[{0}]] {1}\n".format(article['name'],
                                               article['views'])
    return reportcode


def save(site, pagename, report):
    """Save report on the wiki site as pagename."""
    page = site.Pages[pagename]
    page.save(report, summary='Content gap report')

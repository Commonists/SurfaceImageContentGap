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
    """Save report on the wiki site as pagename.
    
    Args:
        site (mwclient.Site): wiki to save to
        pagename (str): name of the page to save the report to
        report (str): surface image content gap report
    """
    page = site.Pages[pagename]
    page.save(report, summary='Content gap report')

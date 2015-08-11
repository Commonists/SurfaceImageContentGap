# -*- coding: utf-8 -*-

"""Search for articles with a given template."""

import logging


import mwclient
import mwclient.listing as listing

LOGGER_NAME = 'sicglog'
LOG = logging.getLogger(LOGGER_NAME)


class ArticleWithTemplate(object):

    """Search article with a given template."""

    def __init__(self, site, templatename):
        """Constructor."""
        self.site = site
        self.templatename = templatename
        if 'Template:' not in templatename:
            self.templatename = 'Template:' + templatename

    def listarticles(self):
        """List of articles containing a given template."""
        # list only namespace 0 for wikipedia articles namespace
        kwargs = dict(listing.List.generate_kwargs('ei', prop='title',
                                                   title=self.templatename,
                                                   namespace=0))
        gen = listing.List(self.site, 'embeddedin', 'ei', **kwargs)
        for info in gen:
            titlename = info['title']
            yield mwclient.page.Page(self.site, titlename)

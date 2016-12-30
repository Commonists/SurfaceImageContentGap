from argparse import ArgumentParser
import datetime
import time


from surfaceimagecontentgap.imagegap import isthereanimage
from surfaceimagecontentgap.bot import SurfaceContentGapBot


def last_rc_time(site):
    """Datetime of last change."""
    rc = site.recentchanges()
    last_rev = rc.next()
    return datetime.datetime \
                   .utcfromtimestamp(time.mktime(last_rev['timestamp']))


def previoushour(dt):
    """One hour previous given datetime."""
    delta = datetime.timedelta(hours=1)
    return dt - delta


def previousday(dt):
    """One day before given datetime."""
    delta = datetime.timedelta(days=1)
    return dt - delta


def rc_from(site, dt):
    """Recent changes from a given datetime."""
    kwargs = {
        'end': dt.strftime('%Y%m%d%H%M%S'),
        'namespace': 0
    }
    rc = site.recentchanges(**kwargs)
    # revisions
    changes = []
    # page titles
    pages = []
    for rev in rc:
        changes.append(rev)
        title = rev['title'].encode('utf-8')
        if title not in pages:
            pages.append(title)
    return {
        'list_revisions': changes,
        'list_pages': pages
    }


def articles_from_titles(site, titles):
    """Articles object from list of titles"""
    return [site.Pages[title.decode('utf-8')] for title in titles]


def list_articles(bot):
    # site
    site = bot.site

    # last hours rc
    end_dt = previoushour(last_rc_time(site))
    recent_changes = rc_from(site, end_dt)
    pages = recent_changes['list_pages']
    return articles_from_titles(site, pages)


def main():
    description = 'Analyzing Wikipedia to surface image content gap (rc).'
    parser = ArgumentParser(description=description)
    parser.add_argument('-w', '--wikipedia',
                        type=str,
                        dest='lang',
                        required=False,
                        default='fr',
                        help='Language code for Wikipedia')
    parser.add_argument('-r', '--report',
                        type=str,
                        dest='report',
                        required=True,
                        help='Page name to write a report.')
    parser.add_argument('-f', '--configfile',
                        type=str,
                        dest='config',
                        required=True,
                        help='Config file with login and password.')
    args = parser.parse_args()
    kwargs = {
        'config_file': args.config,
        'lang': args.lang,
        'report': args.report,
        'list_fun': list_articles,
        'filter_fun': lambda bot, x: not isthereanimage(x),
        'rank_fun': lambda bot, x: 0,
        'frequency': 60
    }
    rc_bot = SurfaceContentGapBot(**kwargs)
    rc_bot.run()


if __name__ == '__main__':
    main()

from argparse import ArgumentParser

import pageviewapi
from surfaceimagecontentgap import logger
from surfaceimagecontentgap.bot import SurfaceContentGapBot
from surfaceimagecontentgap.imagegap import isthereanimage


LOG = logger.logger()


def list_artilces(bot):
    site = bot.site
    titles = []
    random_generator = site.random(0)
    while len(titles) < 1000:
        r = random_generator.next()
        if r['title'] not in titles:
            titles.append(r['title'])
    LOG.info('%d random articles', len(titles))
    return [site.Pages[title] for title in titles]


def pageview90(bot, article):
    project = '{lang}.wikipedia'.format(lang=bot.lang)
    return pageviewapi.period.sum_last(project,
                                       article.name.encode('utf-8'),
                                       last=90,
                                       access='all-access',
                                       agent='all-agents')


def main():
    description = 'Analyzing Wikipedia to surface image content gap (random).'
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
        'list_fun': list_artilces,
        'filter_fun': lambda bot, x: not isthereanimage(x),
        'rank_fun': pageview90,
        'frequency': 60
    }
    lucky_bot = SurfaceContentGapBot(**kwargs)
    lucky_bot.run()


if __name__ == '__main__':
    main()
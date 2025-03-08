import argparse
from datetime import datetime

from devbricksx.common.parser import append_common_developer_options_to_parse
from devbricksx.development.log import set_debug_enabled, set_silent_enabled, debug, info, warn
from devbricksxai.generativeai.genai import init_generative_ai_args, init_generative_ai, \
    create_task_force_from_arguments, print_task_force_info
from devbricksxai.generativeai.roles.artisans.analysts.news.news_ai_analyst import NewsAIAnalyst
from devbricksxai.generativeai.roles.artisans.analysts.news.news_analyst import NewsAnalyst, News
from devbricksxai.generativeai.roles.character import list_characters, Role

DEFAULT_NEWS_ITEM_PER_SOURCE = 5

if __name__ == "__main__":
    ap = argparse.ArgumentParser()

    init_generative_ai_args(ap)

    append_common_developer_options_to_parse(ap)
    ap.add_argument("-ns", "--news-sites",
                    nargs='+',
                    type=str,
                    help="specify the news sites you want to analyze")
    ap.add_argument("-np", "--news-pages",
                    nargs='+',
                    type=str,
                    help="specify the news webpage you want to analyze")
    ap.add_argument("-ips", "--item-per-site",
                    type=int,
                    help="specify maximum number of news items per site")
    ap.add_argument("-nce", "--no-content-extraction",
                    action='store_true',
                    default=False,
                    help="don't extract content from news items")
    ap.add_argument("-na", "--no-analysis",
                    action='store_true',
                    default=False,
                    help="don't analyze news with AI")

    args = ap.parse_args()

    set_debug_enabled(args.verbose)
    if args.silent:
        set_silent_enabled(True)

    init_generative_ai(args)

    task_force = create_task_force_from_arguments("main", args)

    analysts = list_characters(Role.ARTISAN, in_instances=[NewsAnalyst])
    for a in analysts:
        task_force.add_member(a)

    analysts = list_characters(Role.ARTISAN, in_instances=[NewsAIAnalyst])
    for a in analysts:
        task_force.add_member(a)

    print_task_force_info(task_force, debug)

    limit = DEFAULT_NEWS_ITEM_PER_SOURCE
    if args.item_per_site is not None:
        limit = args.item_per_site

    info('==============================================')
    info('|                  Trending                   |')
    info('==============================================')
    info(f'News sites:                   [{args.news_sites}]')
    info(f'News pages:                   [{args.news_pages}]')
    info(f'Max num. of news per site:    [{limit}]')
    info(f'Extract news content:         [{not args.no_content_extraction}]')
    info(f'Analyze news item:            [{not args.no_content_extraction and not args.no_analysis}]')
    info('----------------------------------------------')

    analysts = task_force.select_members(Role.ARTISAN, NewsAnalyst)
    analysts = sorted(analysts, key=lambda x: x.priority, reverse=True)

    extracted_items = []
    if args.news_pages is not None:
        for page in args.news_pages:
            news_item = News()
            news_item.provider = ""

            news_item.link = page

            news_item.title = ""
            news_item.datetime = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            extracted_items += [news_item]

    if args.news_sites is not None:
        for site in args.news_sites:
            debug(f"analyzing site: {site}")

            for analyst in analysts:
                if analyst.can_analyze(site, action = NewsAnalyst.ACTION_EXTRACT_ITEMS):
                    debug(f"using [{analyst.alias}] to extract items from: {site}")

                    items = analyst.craft(data=site, limit=limit)
                    if items is not None and len(items) > 0:
                        extracted_items += items
                        break

    info(f'extracted news items: {len(extracted_items)}')
    info(', '.join(str(item) for item in extracted_items))

    if args.no_content_extraction:
        exit(0)

    analyzed_items = []

    if extracted_items is not None:

        painter = task_force.get_painter()
        in_escort = task_force.get_in_escort()
        out_escort = task_force.get_out_escort()

        for item in extracted_items:
            if item.content is not None and len(item.content) > 0:
                warn(f"skip analyze item: {item.title}, since its content is not empty. content = [{item.content}]")
                analyzed_items.append(item)
            else:
                for analyst in analysts:
                    if analyst.can_analyze(item.link, action = NewsAnalyst.ACTION_ANALYZE_ITEM):
                        debug(f"using [{analyst.alias}] to analyze site: {item.link}")
                        news = analyst.craft(
                            data = item,
                            action = NewsAnalyst.ACTION_ANALYZE_ITEM,
                            painter = painter.alias,
                            in_escort = in_escort.alias,
                            # out_escort = out_escort.alias,
                        )

                        if news is not None:
                            analyzed_items.append(news)
                            break

    info(f'analyzed news items: {len(analyzed_items)}')
    info(', '.join(str(item) for item in analyzed_items))

    if args.no_analysis:
        exit(0)

    advisor = task_force.get_advisor()
    ai_analysts = task_force.select_members(Role.ARTISAN, NewsAIAnalyst)
    ai_analysts = sorted(ai_analysts, key=lambda x: x.priority, reverse=True)
    ai_analyzed_items = []

    if analyzed_items is not None:
        for item in analyzed_items:
            for analyst in ai_analysts:
                if analyst.can_analyze(item):
                    debug(f"using [{analyst.alias}] to analyze site: {item.link}")
                    news = analyst.craft(data = item,
                                         advisor = advisor.alias)

                    if news is not None:
                        ai_analyzed_items.append(news)
                        break

    info(f'AI analyzed news items: {len(ai_analyzed_items)}')
    info(', '.join(str(item) for item in ai_analyzed_items))

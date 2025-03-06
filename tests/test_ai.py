import sys
import os

# 获取 myproject 的绝对路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 添加到 sys.path
sys.path.append(project_root)


import argparse

from devbricksx.common.parser import append_common_developer_options_to_parse
from devbricksx.development.log import set_debug_enabled, set_silent_enabled
from devbricksxai.generativeai.genai import init_generative_ai_args, init_generative_ai, \
    create_task_force_from_arguments

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

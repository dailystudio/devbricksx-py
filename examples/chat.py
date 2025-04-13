import argparse
import uuid

from devbricksx.common.parser import append_common_developer_options_to_parse
from devbricksx.development.log import set_debug_enabled, set_silent_enabled, info, error
from devbricksxai.generativeai.genai import init_generative_ai_args, init_generative_ai, \
    create_task_force_from_arguments

if __name__ == "__main__":
    ap = argparse.ArgumentParser()

    init_generative_ai_args(ap)

    append_common_developer_options_to_parse(ap)

    args = ap.parse_args()

    set_debug_enabled(args.verbose)
    if args.silent:
        set_silent_enabled(True)

    init_generative_ai(args)

    task_force = create_task_force_from_arguments("main", args)

    session_id = str(uuid.uuid4())
    info(f"start a session id: {session_id}")

    advisor = task_force.get_advisor()
    info(f"advisor: {advisor}")

    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ["exit", "quit"]:
                info("exiting chat.")
                break
            ret = advisor.craft(prompt=user_input, session=session_id)
            info(f"{advisor.name}: {ret}")

        except KeyboardInterrupt:
            info("\ninterrupted by user. Exiting.")
            break
        except Exception as e:
            error(f"Error: {e}")



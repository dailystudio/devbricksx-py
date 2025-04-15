import argparse
import uuid
import re
from pyexpat import model

from devbricksx.common.parser import append_common_developer_options_to_parse
from devbricksx.development.log import set_debug_enabled, set_silent_enabled, info, error, warn
from devbricksxai.generativeai.genai import init_generative_ai_args, init_generative_ai, \
    create_task_force_from_arguments

def extract_code(raw_text):
    extracted_code = {
        'html': [],
        'css': [],
        'javascript': []
    }

    try:
        pattern = re.compile(
            r'```(html|css|javascript|js)\n(.*?)```',
            flags=re.IGNORECASE | re.DOTALL
        )

        for match in pattern.finditer(raw_text):
            language = match.group(1).lower().strip()  # Get language, lowercase it
            code = match.group(2).strip()  # Get code content

            if language == 'js':
                language = 'javascript'

            if language in extracted_code:
                extracted_code[language].append(code)
    except Exception as err:
        warn(f"[{model}] failed to extract code from : {err}")

    return extracted_code

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

            extracted_content = extract_code(ret)
            html_code = extracted_content['html'][0] if extracted_content['html'] else None
            js_code = extracted_content['javascript'][0] if extracted_content['javascript'] else None
            css_code = extracted_content['css'][0] if extracted_content['css'] else None
            if html_code is not None and len(html_code) > 0:
                info(f"HTML: {html_code}")
            if js_code is not None and len(js_code) > 0:
                info(f"Javascript: {js_code}")
            if css_code is not None and len(css_code) > 0:
                info(f"CSS: {css_code}")

        except KeyboardInterrupt:
            info("\ninterrupted by user. Exiting.")
            break
        except Exception as e:
            error(f"Error: {e}")



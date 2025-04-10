import openai

from devbricksxai.generativeai.roles.advisor import Advisor
from devbricksxai.generativeai.settings.aisettings import get_ai_settings
from devbricksx.development.log import info, debug

ADVISOR_GPT = 'ChatGPT'
__ADVISOR_PROVIDER__ = 'OpenAI.com'

class ChatGPTAdvisor(Advisor):

    PARAM_CONTEXT = 'context'
    PARAM_MODEL = 'model'
    PARAM_API_KEY = 'apikey'

    ROLE_TAG_USER = 'user'
    ROLE_TAG_ADVISOR = 'assistant'
    ROLE_TAG_OTHERS = 'system'

    def __init__(self):
        super().__init__(ADVISOR_GPT, __ADVISOR_PROVIDER__)
        # openai.api_key = get_ai_settings().open_ai_apikey

    def get_role_tag(self, role):
        if role == Advisor.ROLE_USER:
            return self.ROLE_TAG_USER
        elif role == Advisor.ROLE_ADVISOR:
            return self.ROLE_TAG_ADVISOR
        else:
            return self.ROLE_TAG_OTHERS

    def ask(self, prompt, **kwargs):
        openai.api_key = self.get_parameter(ChatGPTAdvisor.PARAM_API_KEY)
        debug("OPEN AI API Key: {}".format(openai.api_key))

        model = self.get_parameter(ChatGPTAdvisor.PARAM_MODEL)
        if model is None:
            model = get_ai_settings().open_ai_model

        messages = kwargs.get(Advisor.PARAM_HISTORIES, None)
        if messages is None:
            messages = []

        messages.append({ "role": self.ROLE_TAG_USER, "content": prompt })

        # context = self.get_parameter(ChatGPTAdvisor.PARAM_CONTEXT)
        # if context is not None:
        #     messages = context + messages

        debug("[{}] be asked: {}".format(model, messages))

        try:
            completion_of_title = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                # response_format={"type": "json_object"},
            )

            result = completion_of_title.choices[0].message.content.strip()
        except Exception as err:
            info('ask GPT [{}] completion failed: {}'.format(model, err))
            result = None

        info("[{}] answers: {}".format(model, result))

        return result

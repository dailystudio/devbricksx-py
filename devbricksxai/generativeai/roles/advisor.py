from abc import abstractmethod, ABC

from devbricksxai.generativeai.roles.character import Character, Role


class Advisor(Character, ABC):
    PARAM_PROMPT = 'prompt'

    def __init__(self, name, provider):
        super().__init__(name, provider, Role.ADVISOR)

    @abstractmethod
    def ask(self, prompt, **kwargs):
        pass

    def craft(self, **kwargs):
        prompt = kwargs.pop(Advisor.PARAM_PROMPT)
        if prompt is None:
            raise ValueError(
                f"craft() of {self.__class__.__name__} must include [{Advisor.PARAM_PROMPT}] in arguments.")

        return self.ask(prompt, **kwargs)

def init_advisors():
    from generativeai.roles.character import register_character
    from generativeai.roles.advisors.chatgpt import ChatGPTAdvisor

    register_character(ChatGPTAdvisor())
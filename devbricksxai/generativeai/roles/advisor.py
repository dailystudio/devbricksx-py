from abc import abstractmethod, ABC

from devbricksxai.generativeai.roles.character import Character, Role


class Advisor(Character, ABC):
    PARAM_PROMPT = 'prompt'
    PARAM_HISTORIES = 'histories'
    PARAM_SESSION = 'session'

    ROLE_USER = 'user'
    ROLE_ADVISOR = 'advisor'

    session_histories = {}

    def __init__(self, name, provider):
        super().__init__(name, provider, Role.ADVISOR)

    @abstractmethod
    def ask(self, prompt, **kwargs):
        pass

    @abstractmethod
    def get_role_tag(self, role):
        pass

    def format_histories(self, histories):
        formatted_histories = []
        for history in histories:
            role = history["role"]
            formatted_role = self.get_role_tag(role)
            formatted_histories.append(
                {"role": formatted_role, "content": history["content"]}
            )

        return formatted_histories

    def format_prompt(self, prompt):
        if isinstance(prompt, str):
            result = prompt
        elif isinstance(prompt, list):
            result = ", ".join(prompt)  # 或者用其他分隔符
        else:
            result = str(prompt)  # 可选：处理其他类型
        return result

    def craft(self, **kwargs):
        prompt = kwargs.pop(Advisor.PARAM_PROMPT)
        if prompt is None:
            raise ValueError(
                f"craft() of {self.__class__.__name__} must include [{Advisor.PARAM_PROMPT}] in arguments.")

        formated_prompt = self.format_prompt(prompt)

        session = kwargs.get(Advisor.PARAM_SESSION)
        if session is not None:
            histories = self.session_histories[session]
            if histories is None:
                histories = []

            kwargs[Advisor.PARAM_HISTORIES] = self.format_histories(histories)
            ret = self.ask(formated_prompt, **kwargs)

            if ret is not None and len(ret) > 0:
                histories.append({"role": self.ROLE_USER, "content": prompt})
                histories.append({"role": self.ROLE_ADVISOR, "content": ret})

            return ret
        else:
            return self.ask(formated_prompt, **kwargs)

def init_advisors():
    from devbricksxai.generativeai.roles.character import register_character
    from devbricksxai.generativeai.roles.advisors.chatgpt import ChatGPTAdvisor

    register_character(ChatGPTAdvisor())
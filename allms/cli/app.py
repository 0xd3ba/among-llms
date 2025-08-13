from textual.app import App

from allms.config import AppConfiguration


class AmongLLMs(App):
    def __init__(self, ai_model: str, ai_reasoning_lvl: str, max_agent_count: int):
        super().__init__()
        self._ai_model = ai_model
        self._ai_reasoning_lvl = ai_reasoning_lvl
        self._max_agent_count = max_agent_count

        # TODO: Write the rest of the app

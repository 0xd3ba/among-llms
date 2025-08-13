from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Vertical

from allms.config import RunTimeConfiguration


class MainScreen(Screen):
    """ Home-screen of the application """
    def __init__(self, config: RunTimeConfiguration, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._config = config

    def compose(self) -> ComposeResult:
        # TODO: Build the screen
        yield Vertical()

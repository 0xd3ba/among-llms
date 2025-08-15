from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer

from allms.config import RunTimeConfiguration
from allms.cli.widgets.chat import ChatroomWidget
from allms.core.state import GameStateManager


class ChatroomScreen(Screen):
    """ Class for the main chatroom screen """
    # TODO: Need to support taking chat data as argument for loading a saved chat
    def __init__(self, config: RunTimeConfiguration, state_manager: GameStateManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._config = config
        self._state_manager = state_manager

    def compose(self) -> ComposeResult:
        yield ChatroomWidget(self._config, self._state_manager)
        yield Footer()

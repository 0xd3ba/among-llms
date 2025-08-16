from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Label, Footer

from allms.config import BindingConfiguration, RunTimeConfiguration
from allms.cli.widgets.new import NewChatroomWidget
from allms.core.state import GameStateManager


class NewChatScreen(ModalScreen):
    """ Screen for creating new chatroom """

    def __init__(self, title: str, config: RunTimeConfiguration, state_manager: GameStateManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._title = title
        self._config = config
        self._state_manager = state_manager
        self._new_chatroom_widget = NewChatroomWidget(self._title, self._config, self._state_manager)

    def compose(self) -> ComposeResult:
        yield self._new_chatroom_widget
        yield Footer()

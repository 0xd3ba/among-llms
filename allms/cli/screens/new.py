from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Label, Footer

from allms.config import RunTimeConfiguration
from allms.cli.widgets.new import NewChatroomWidget


class NewChatScreen(ModalScreen):
    """ Screen for creating new chatroom """
    def __init__(self, title: str, config: RunTimeConfiguration, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._title = title
        self._config = config

    def compose(self) -> ComposeResult:
        yield NewChatroomWidget(self._title, self._config)
        yield Footer()

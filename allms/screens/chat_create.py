from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Label
from textual.containers import Horizontal

from allms.config import AppConfiguration
from allms.widgets.chat_create import CreateNewChatWidget


class CreateNewChatScreen(ModalScreen):
    """ Screen displayed when user clicks new chat button """

    BINDINGS = [
        # TODO: Add the bindings
    ]

    def __init__(self):
        super().__init__()

    def compose(self) -> ComposeResult:
        yield CreateNewChatWidget()

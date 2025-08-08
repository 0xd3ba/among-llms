from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Static, Label


class ChatSidebarWidget(Vertical):
    """ Class for the chat sidebar widget """
    def __init__(self):
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Label()

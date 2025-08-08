from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Static, Label


class ChatContentWidget(Vertical):
    """ Class for the chat content widget """
    def __init__(self):
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Label()

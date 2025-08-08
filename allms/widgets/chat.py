from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Static


class ChatWidget(Static):
    """ Class for the main chat screen """
    def __init__(self):
        super().__init__()

    def compose(self) -> ComposeResult:
        # TODO: Implement the chat screen
        yield Horizontal()

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical

from .chat_content import ChatContentWidget
from .chat_sidebar import ChatSidebarWidget


class ChatWidget(Horizontal):
    """ Class for the main chat widget comprising sidebar and chat contents """
    def __init__(self):
        super().__init__()

    def compose(self) -> ComposeResult:
        yield ChatSidebarWidget()
        yield ChatContentWidget()

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical

from .chat_manager import ChatContentManagerWidget
from .chat_sidebar import ChatSidebarWidget


class ChatWidget(Horizontal):
    """ Class for the main chat widget comprising sidebar and chat contents """
    def __init__(self):
        super().__init__()
        self._sidebar = ChatSidebarWidget()
        self._content_mgr = ChatContentManagerWidget()

    def compose(self) -> ComposeResult:
        yield self._sidebar
        yield self._content_mgr

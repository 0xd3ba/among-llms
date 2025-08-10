from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, Container
from textual.widgets import Static, Label

from .chat_content import ChatContentWidget


class ChatContentManagerWidget(Container):
    """ Class for the chat content parent container """
    def __init__(self):
        super().__init__()
        self._active_chat: Container = ChatContentWidget(contents=None)

    def compose(self) -> ComposeResult:
        yield self._active_chat

    def switch(self, widget: Container):
        assert widget is not None, f"Expecting a widget to switch into but received None instead"
        self._active_chat.remove()
        self._active_chat = widget
        self.mount(widget)

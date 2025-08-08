from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Static, Label

from .components.chat_list import ChatListComponent
from .components.chat_new import NewChatRoomButtonComponent


class ChatSidebarWidget(Vertical):
    """ Class for the chat sidebar widget """
    def __init__(self):
        super().__init__()
        self._chat_list = ChatListComponent()
        self._new_chatroom_btn = NewChatRoomButtonComponent("New Chatroom [+]")

    def compose(self) -> ComposeResult:
        yield self._chat_list
        yield self._new_chatroom_btn

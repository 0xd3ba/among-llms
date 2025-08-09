from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button

from allms.screens.chat_create import CreateNewChatScreen
from .components.chat_list import ChatListComponent
from .components.chat_new import NewChatRoomButtonComponent


class ChatSidebarWidget(Vertical):
    """ Class for the chat sidebar widget """
    def __init__(self):
        super().__init__()
        self._new_chatroom_btn_id = "new_chat"
        self._chat_list = ChatListComponent()
        self._new_chatroom_btn = NewChatRoomButtonComponent("New Chatroom [+]", variant="primary", id=self._new_chatroom_btn_id)

    def compose(self) -> ComposeResult:
        yield self._chat_list
        yield self._new_chatroom_btn

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == self._new_chatroom_btn_id:
            # TODO: Pass an object to populate it with the chat configuration
            self.app.push_screen(CreateNewChatScreen())

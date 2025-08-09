from textual import events
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Label


class NewChatRoomButtonComponent(Button):
    """ Class for the creating a new chatroom """
    def __init__(self, button_name: str, *args, **kwargs):
        super().__init__(button_name, *args, **kwargs)

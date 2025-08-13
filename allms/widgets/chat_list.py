from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll, Container
from textual.widgets import Label, Button, Footer, OptionList

from allms.config import AppConfiguration, StyleConfiguration
from allms.widgets.components.chat_list import ChatOptionsListComponent


class ChatOptionsList(OptionList):
    """ Class for the displaying and selecting from a list of historical chats """
    def __init__(self, data: list[dict] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # TODO: Write a custom class for handling chat data
        self._data = data

    def on_mount(self) -> None:
        self.clear_options()
        # TODO: Add actual chats later on -- for now, just add placeholders
        self.add_options([ChatOptionsListComponent({}) for _ in range(5)])

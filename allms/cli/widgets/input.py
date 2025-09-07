from typing import Type, Callable

from textual.binding import Binding
from textual.widgets import Input

from allms.config import BindingConfiguration


class MessageBox(Input):
    """ Class for message box in the chat screen """

    BINDINGS = [
        Binding(BindingConfiguration.chatroom_send_message, "send_message", "Send Message", priority=True)
    ]

    def __init__(self, on_send_callback: Type[Callable], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._on_send = on_send_callback  # Callback method from the parent

    def action_send_message(self) -> None:
        """ Invoked when key binding for send is pressed """
        self._on_send()

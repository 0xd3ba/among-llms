from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, Container
from textual.widgets import Static, Label, Input, Button

from .components.selection import SelectComponent
from allms.config import AppConfiguration, StyleConfiguration


class ChatContentSendWidget(Horizontal):
    """ Class for the widget hosting the input box, send-as and send buttons """
    def __init__(self, contents: dict | None):
        super().__init__()

        self._is_disabled = (contents is None)
        # TODO: Create a hotkey class in config and refer its value in the string
        self._input_area = Input(placeholder="Type your message [Ctrl+Enter to send]", disabled=self._is_disabled)

        send_as_choices = ["-"] if self._is_disabled else ["You"]  # TODO: Extract this from contents
        self._send_as_list = SelectComponent(send_as_choices, is_compact=False, disabled=self._is_disabled)

    def compose(self) -> ComposeResult:
        yield self._input_area
        yield self._send_as_list


class ChatNoContent(Container):
    """ Placeholder class when no chat is selected and there is nothing to display """
    def compose(self) -> ComposeResult:
        with Vertical() as v:
            v.add_class(StyleConfiguration.css_class_round_border)

            app_name = AppConfiguration.app_name
            v.border_title = f"Welcome to {app_name}!"

            tagline_text = AppConfiguration.app_tagline
            tagline_text = f"[i]{tagline_text}[/]"

            yield Static(tagline_text, id="no-content-tagline")


class ChatContentWidget(Container):
    """ Class for the main chat contents """
    def __init__(self, contents: dict | None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # TODO: Wrap contents in a custom class
        self._contents = contents
        self._send_widget = ChatContentSendWidget(self._contents)

    def compose(self) -> ComposeResult:
        yield ChatNoContent()  # TODO: Return a different container if contents is not None
        yield self._send_widget

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Input, TextArea

from allms.config import StyleConfiguration


class TextAreaComponent(Vertical):
    """ Class for user-input textbox """

    def __init__(self, title: str = "", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.border_title = title

    def on_mount(self) -> None:
        self.add_class(StyleConfiguration.css_class_round_border)
        self.add_class(StyleConfiguration.css_class_highlight_border_on_focus)

    def compose(self) -> ComposeResult:
        yield TextArea(show_line_numbers=True)

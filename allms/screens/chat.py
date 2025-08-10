from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Label
from textual.containers import Horizontal

from allms.widgets.app_header import AppHeaderWidget
from allms.config import AppConfiguration
from allms.widgets.chat import ChatWidget


class MainChatScreen(Screen):
    """ Main screen of the UI """

    AUTO_FOCUS = None

    def __init__(self):
        super().__init__()

    def compose(self) -> ComposeResult:
        yield AppHeaderWidget()
        yield ChatWidget()

        footer = Footer()
        footer.compact = "compact"

        yield footer

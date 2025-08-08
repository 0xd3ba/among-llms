from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Label, TabbedContent
from textual.containers import Horizontal, Vertical

from allms.config import AppConfiguration
from allms.widgets.clock import ClockWidget
from allms.widgets.chat import ChatWidget


class ClockHeader(Horizontal):
    """ Class for clock header """
    def compose(self) -> ComposeResult:
        yield ClockWidget(AppConfiguration.clock)


class AppHeader(Horizontal):
    """ Class for header of the application """

    def compose(self) -> ComposeResult:
        yield Label(f"[b]{AppConfiguration.app_name}[/] [dim]v{AppConfiguration.app_version}[/]", id="app-header")
        yield ClockHeader(id="clock-header")


class ChatScreen(Screen):
    """ Main screen of the UI """

    AUTO_FOCUS = None

    def __init__(self):
        super().__init__()

    def compose(self) -> ComposeResult:
        yield AppHeader()
        yield ChatWidget()

        footer = Footer()
        footer.compact = "compact"

        yield footer

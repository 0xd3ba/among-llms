from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Label

from allms.config import AppConfiguration
from .clock import ClockWidget


class AppHeaderWidget(Horizontal):
    """ Class for header of the application """
    def compose(self) -> ComposeResult:
        yield Label(f"[b]{AppConfiguration.app_name}[/] [dim]v{AppConfiguration.app_version}[/]", id="app-header")
        yield ClockWidget(id="clock-header")

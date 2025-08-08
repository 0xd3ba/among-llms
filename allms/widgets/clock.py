from textual.app import ComposeResult
from textual.containers import Horizontal

from allms.config import AppConfiguration
from .components.clock import ClockWidgetComponent


class ClockWidget(Horizontal):
    """ Class for clock widget """
    def compose(self) -> ComposeResult:
        yield ClockWidgetComponent(AppConfiguration.clock)

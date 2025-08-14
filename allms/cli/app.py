from pathlib import Path

from textual import log
from textual.app import App
from textual.screen import Screen

from allms.config import AppConfiguration, RunTimeConfiguration
from .screens.main import MainScreen


class AmongLLMs(App):

    AUTO_FOCUS = None
    ROOT_CSS_PATH = Path(__file__).parent / "css"
    CSS_PATH = [
        # Note: Ordering matters
        ROOT_CSS_PATH / "main.scss",
    ]

    BINDINGS = [
        # TODO: Create the bindings
    ]

    def __init__(self, config: RunTimeConfiguration):
        super().__init__()
        self._config = config
        self._main_screen = MainScreen(self._config)

    def on_ready(self) -> None:
        msg = f"Start time: {AppConfiguration.clock.current_time_in_iso_format()}"
        log.debug(msg)

    def get_default_screen(self) -> Screen:
        return self._main_screen

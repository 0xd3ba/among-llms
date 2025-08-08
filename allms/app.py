from pathlib import Path

from textual import log
from textual.app import App
from textual.screen import Screen

from .config import AppConfiguration
from .screens.chat import ChatScreen


class AmongLLMs(App):
    """ Main class of the app """

    AUTO_FOCUS = None
    ROOT_CSS_PATH = Path(__file__).parent / "css"
    CSS_PATH = [
        # Note: Ordering matters
        ROOT_CSS_PATH / "global.scss",
        ROOT_CSS_PATH / "header.scss",
    ]

    BINDINGS = [
        # TODO: Create the bindings
    ]

    def __init__(self):
        super().__init__()

    def on_ready(self) -> None:
        msg = f"Start time: {AppConfiguration.clock.current_time_in_iso_format()}"
        log.debug(msg)

    def get_default_screen(self) -> Screen:
        return ChatScreen()

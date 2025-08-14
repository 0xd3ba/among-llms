from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Vertical, VerticalScroll
from textual.widgets import Footer, Static

from allms.config import AppConfiguration, RunTimeConfiguration
from allms.cli.widgets.banner import BannerWidget
from allms.cli.widgets.main_menu import MainMenuOptionListWidget


class MainScreen(Screen):
    """ Home-screen of the application """
    def __init__(self, config: RunTimeConfiguration, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._config = config
        self._options = {
            # Main-menu option: Widget that is instantiated when option is clicked
            # TODO: Map the containers to their respective item
            "New Chatroom":  None,
            "Load Chatroom": None,
            "Quit": None
        }

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="main-screen-container"):
            yield BannerWidget(self._config)
            with Vertical(id="main-screen-option-container"):
                yield MainMenuOptionListWidget(self._config, self._options)

        yield Footer()

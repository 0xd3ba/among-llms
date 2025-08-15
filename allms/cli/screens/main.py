from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Vertical, VerticalScroll
from textual.widgets import Footer, Static

from allms.config import AppConfiguration, RunTimeConfiguration
from allms.cli.screens.new import NewChatScreen
from allms.cli.widgets.banner import BannerWidget
from allms.cli.widgets.home import MainMenuOptionListWidget
from allms.core.state import GameStateManager


class MainScreen(Screen):
    """ Home-screen of the application """
    def __init__(self, config: RunTimeConfiguration, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._config = config
        self._options = {
            # Main-menu option: Widget that is instantiated when option is clicked
            # TODO: Map the handlers to their respective item
            "New Chatroom":  self.handler_new_chatroom,
            "Load Chatroom": self.handler_load_chatroom,
            "Quit": self.handler_quit
        }

        self._state_manager = GameStateManager(self._config)

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="main-screen-container"):
            yield BannerWidget(self._config)
            with Vertical(id="main-screen-option-container"):
                yield MainMenuOptionListWidget(self._config, self._options)

        yield Footer()

    async def handler_new_chatroom(self, option_item: str) -> None:
        await self.app.push_screen(NewChatScreen(option_item, self._config, self._state_manager))

    async def handler_load_chatroom(self, option_item: str) -> None:
        raise NotImplementedError

    async def handler_quit(self, option_item: str) -> None:
        self.app.exit()

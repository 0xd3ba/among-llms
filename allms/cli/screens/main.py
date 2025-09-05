from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.containers import Vertical, VerticalScroll
from textual.widgets import Footer

from allms.config import AppConfiguration, BindingConfiguration, RunTimeConfiguration
from allms.cli.screens.about import AboutAppScreen
from allms.cli.screens.chat import ChatroomScreen
from allms.cli.screens.load import LoadGameStateScreen
from allms.cli.screens.new import NewChatScreen
from allms.cli.screens.splash import MainSplashScreen
from allms.cli.widgets.banner import BannerWidget
from allms.cli.widgets.home import MainMenuOptionListWidget
from allms.core.state import GameStateManager


class MainScreen(Screen):
    """ Home-screen of the application """

    BINDINGS = [
        Binding(BindingConfiguration.main_show_about, "show_about_screen", "About"),
        Binding(BindingConfiguration.chatroom_quit, "quit", "Quit")
    ]

    def __init__(self, config: RunTimeConfiguration, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._config = config
        self._options = {
            # Main-menu option: Widget that is instantiated when option is clicked
            "New Chatroom":  self.handler_new_chatroom,
            "Load Chatroom": self.handler_load_chatroom,
            "Quit": self.handler_quit
        }

        self._state_manager = GameStateManager(self._config)

    def on_mount(self) -> None:
        if self._config.skip_intro:
            return
        self.app.push_screen(MainSplashScreen())

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="main-screen-container"):
            yield BannerWidget(self._config)
            with Vertical(id="main-screen-option-container"):
                yield MainMenuOptionListWidget(self._config, self._options)

        yield Footer()

    async def handler_new_chatroom(self, option_item: str) -> None:
        await self.app.push_screen(NewChatScreen(option_item, self._config, self._state_manager))

    async def handler_load_chatroom(self, option_item: str) -> None:
        await self.app.push_screen(
            LoadGameStateScreen(
                option_item, self._config, self._state_manager,
                widget_params=dict(on_confirm_callback=self.__load_chatroom)
            )
        )

    async def handler_quit(self, option_item: str) -> None:
        self.app.exit()

    async def action_quit(self) -> None:
        """ Invoked when binding for exit is pressed """
        await self.handler_quit("")

    def action_show_about_screen(self) -> None:
        """ Invoked when binding for showing about screen is pressed """
        title = "About"
        screen = AboutAppScreen(title=title, config=self._config, state_manager=self._state_manager)
        self.app.push_screen(screen)

    def __load_chatroom(self, state_path: Path) -> None:
        """ Callback method invoked when load is successful """
        self._state_manager.load(file_path=state_path)
        # If no error, we can start the chatroom screen
        self.app.pop_screen()  # Close the loading screen

        AppConfiguration.logger.log(f"Parsing game-state successful. Loading chatroom ...")
        is_disabled = self._state_manager.get_game_ended()
        screen = ChatroomScreen(config=self._config, state_manager=self._state_manager, is_disabled=is_disabled)
        self.app.push_screen(screen)

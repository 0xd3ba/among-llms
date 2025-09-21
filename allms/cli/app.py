from pathlib import Path

from textual.app import App
from textual.screen import Screen

from allms.config import AppConfiguration, RunTimeConfiguration
from .screens.main import MainScreen
from .themes import CustomThemeFactory


class AmongLLMs(App):

    AUTO_FOCUS = None
    ROOT_CSS_PATH = Path(__file__).parent / "css"
    CSS_PATH = [
        # Note: Ordering matters
        ROOT_CSS_PATH / "global.scss",
        ROOT_CSS_PATH / "main.scss",
        ROOT_CSS_PATH / "new.scss",
        ROOT_CSS_PATH / "chat.scss",
        ROOT_CSS_PATH / "contents.scss",
        ROOT_CSS_PATH / "ended.scss"
    ]

    def __init__(self, config: RunTimeConfiguration):
        super().__init__()
        self._config = config
        self._main_screen = MainScreen(self._config)

    def on_mount(self):
        # Register and set the theme
        themes = CustomThemeFactory.get_all_themes()
        for theme in themes:
            AppConfiguration.logger.log(f"Registering the following custom theme: {theme.name}")
            self.register_theme(theme)

        self.theme = self._config.theme

    def on_ready(self) -> None:
        msg = f"Start time: {AppConfiguration.clock.current_time_in_iso_format()}"
        AppConfiguration.logger.log(msg)

    def get_default_screen(self) -> Screen:
        return self._main_screen

from textualeffects.widgets import SplashScreen

from allms.config import AppConfiguration
from allms.cli.banner import Banner
from allms.cli.effects import TextualEffects


class MainSplashScreen(SplashScreen):
    def __init__(self):
        effect, config = TextualEffects.get_random_effect()

        app_dev = AppConfiguration.app_dev
        app_lines = [f"--+ by {app_dev} +--"]

        banner_text = Banner.splash_banner
        banner_text = Banner.add_border(
            content=banner_text,
            additional_lines=app_lines,
            border_char="",
            # Add padding for more animation
            hpad=20,
            vpad=1
        )

        super().__init__(text=banner_text, effect=effect, config=config)

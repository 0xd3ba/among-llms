from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static

from allms.cli.banner import Banner
from allms.config import AppConfiguration, RunTimeConfiguration


class BannerWidget(Vertical):

    def __init__(self, config: RunTimeConfiguration, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._config = config

    def on_mount(self) -> None:
        self.can_focus = False

    def compose(self) -> ComposeResult:
        hackathon = f"-- {AppConfiguration.app_hackathon} --"
        yield Static(hackathon)

        app_version = f"v{AppConfiguration.app_version}"
        app_ai_model = f"Powered by {self._config.ai_model}"
        banner_fmt = Banner.add_border(Banner.main_banner,
                                       additional_lines=[app_version, "\n", app_ai_model],
                                       hpad=2, vpad=0, pad_bottom=False)
        yield Static(banner_fmt)
        for line in AppConfiguration.app_tagline:
            yield Static(line)
        yield Static("\n")

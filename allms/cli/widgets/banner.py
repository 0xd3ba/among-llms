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
        app_ai_model = self.__get_ai_models()
        banner_fmt = Banner.add_border(Banner.main_banner,
                                       additional_lines=[app_version, "\n", *app_ai_model],
                                       hpad=2, vpad=0, pad_bottom=False)
        yield Static(banner_fmt)
        for line in AppConfiguration.app_tagline:
            yield Static(line)
        yield Static("\n")

    def __get_ai_models(self, max_models_per_line: int = 3) -> list[str]:
        """ Returns a string 'Powered by X' with the AI models """
        prefix_str = "Powered by"
        models = [model.name for model in self._config.use_models]

        if len(models) == 1:
            return [f"{prefix_str} {models[0]}"]

        # Limit N number of models displayed in each line
        # Pad the model names so that they appear nicely
        max_len = max(len(m) for m in models)
        fmt_models = [m.ljust(max_len) for m in models]

        fmt_lines: list[str] = [prefix_str]
        for i in range(0, len(models), max_models_per_line):
            chunk = fmt_models[i: i+max_models_per_line]
            fmt_line = "\n" + " | ".join(chunk)
            fmt_lines.append(fmt_line)

        return fmt_lines

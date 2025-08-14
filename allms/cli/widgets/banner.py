from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static

from allms.config import AppConfiguration, RunTimeConfiguration


banner = r"""
░█▀█░█▄█░█▀█░█▀█░█▀▀░░░█░░░█░░░█▄█░█▀▀
░█▀█░█░█░█░█░█░█░█░█░░░█░░░█░░░█░█░▀▀█
░▀░▀░▀░▀░▀▀▀░▀░▀░▀▀▀░░░▀▀▀░▀▀▀░▀░▀░▀▀▀        
"""


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
        banner_fmt = self.__add_border(banner,
                                       additional_lines=[app_version, "\n", app_ai_model],
                                       hpad=2, vpad=0, pad_bottom=False)
        yield Static(banner_fmt)
        for line in AppConfiguration.app_tagline:
            yield Static(line)
        yield Static("\n")

    @staticmethod
    def __add_border(content: str,
                     additional_lines: list[str] = None,
                     border_char: str = "*",
                     hpad: int = 0,
                     vpad: int = 0,
                     pad_top: bool = True,
                     pad_bottom: bool = True
                     ) -> str:
        """ Helper method to add border to the given content string """
        lines = content.splitlines()
        if additional_lines is not None:
            lines.extend(additional_lines)

        max_len = max(len(line) for line in lines)

        border_width = max_len + 2 * hpad + 2
        top_btm_border = border_char * border_width

        empty_line = f"{border_char}{' ' * (border_width - 2)}{border_char}"
        vpad_lines = [empty_line] * vpad

        # Pad each line horizontally to center text
        padded_lines = []
        for line in lines:
            line = line.strip()
            total_pad = max_len - len(line)
            left_pad = total_pad // 2 + hpad
            right_pad = total_pad - (total_pad // 2) + hpad

            if line:
                padded_lines.append(f"{border_char}{' ' * left_pad}{line}{' ' * right_pad}{border_char}")
            else:
                padded_lines.append(empty_line)

        fmt_lines = [top_btm_border]
        if pad_top:
            fmt_lines += vpad_lines
        fmt_lines += padded_lines
        if pad_bottom:
            fmt_lines += vpad_lines
        fmt_lines += [top_btm_border]

        result = "\n".join(fmt_lines)
        result = "\n" + result + "\n"

        return result

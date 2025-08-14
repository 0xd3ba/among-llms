from dataclasses import dataclass

from rich.console import Console, ConsoleOptions, RenderResult
from rich.text import Text
from textual.containers import Container
from textual.reactive import reactive
from textual.widgets import OptionList
from textual.widgets.option_list import Option


@dataclass
class MainMenuOptionItemRenderable:
    """ Class for rendering each main-menu item in the list """
    item_text: str

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        yield Text(self.item_text)


class MainMenuOptionItem(Option):
    """ Class for each main-menu item in the list """
    def __init__(self, item_text: str, item_widget: Container):
        super().__init__(MainMenuOptionItemRenderable(item_text))
        self._item_text = item_text
        self._item_widget = item_widget


class MainMenuOptionListWidget(OptionList):

    """ Class for main-menu widget displaying list of options """
    def __init__(self, option_map: dict[str, Container], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._option_map = option_map
        assert len(option_map) > 0, f"Expected main-menu items to be > 0 but got no items"

    def on_mount(self) -> None:
        self.clear_options()
        option_items = [MainMenuOptionItem(option, widget) for (option, widget) in self._option_map.items()]
        self.add_options(option_items)

        max_len = max([len(t) for t in self._option_map]) + 10
        self.styles.min_width = max_len
        self.styles.max_width = max_len

        self.highlighted = 0
        self.focus()

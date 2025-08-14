from dataclasses import dataclass
from typing import Callable

from rich.console import Console, ConsoleOptions, RenderResult
from rich.text import Text
from textual import on
from textual.widgets import OptionList
from textual.widgets.option_list import Option

from allms.config import RunTimeConfiguration


@dataclass
class MainMenuOptionItemRenderable:
    """ Class for rendering each main-menu item in the list """
    item_text: str

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        yield Text(self.item_text, justify="center")


class MainMenuOptionItem(Option):
    """ Class for each main-menu item in the list """
    def __init__(self, item_text: str, item_handler: Callable):
        super().__init__(MainMenuOptionItemRenderable(item_text))
        self.item_text = item_text
        self.item_handler = item_handler


class MainMenuOptionListWidget(OptionList):
    """ Class for main-menu widget displaying list of options """
    def __init__(self, config: RunTimeConfiguration, option_map: dict[str, Callable], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._config = config
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

    @on(OptionList.OptionSelected)
    async def handler_option_selected(self, event: OptionList.OptionSelected) -> None:
        """ Handler for handling events when an item is selected """
        item_selected = event.option.item_text
        assert item_selected in self._option_map, f"Item({item_selected}) is not present in the map"
        assert self._option_map[item_selected] is not None, f"Item({item_selected}) doesn't have an associated handler in the map"

        await self._option_map[item_selected](item_selected)

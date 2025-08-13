from rich.console import Console, ConsoleOptions, RenderResult
from rich.panel import Panel
from rich.text import Text
from textual.widgets.option_list import Option


class _ChatItemRenderable:
    def __init__(self, data: dict):
        # TODO: Write a custom class for handling chat data
        self._data = data

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        yield Panel(
            Text("Test-item")  # TODO: Handle this better later on. For now, just a placeholder
        )


class ChatOptionsListComponent(Option):
    """ Class for a single chat item """
    def __init__(self, data: dict, *args, **kwargs):
        super().__init__(_ChatItemRenderable(data), *args, **kwargs)
        # TODO: Write a custom class for handling chat data
        self._data = data

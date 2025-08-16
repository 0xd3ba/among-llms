from textual.app import ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import TextArea

from allms.config import RunTimeConfiguration
from allms.core.state import GameStateManager
from .modal import ModalScreenWidget


class ChatScenarioWidget(ModalScreenWidget):

    def __init__(self, title: str, config: RunTimeConfiguration, state_manager: GameStateManager, *args, **kwargs):
        super().__init__(title, config, state_manager, *args, **kwargs)
        self._scenario = self._state_manager.get_scenario()

    def compose(self) -> ComposeResult:
        textbox = TextArea(text=self._scenario, show_line_numbers=True, read_only=True)
        with VerticalScroll():
            yield self._wrap_inside_container(textbox, Horizontal, border_title="")

        textbox.focus()

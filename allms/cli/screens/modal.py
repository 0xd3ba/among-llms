from typing import Type

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.containers import Container
from textual.widgets import Footer

from allms.config import RunTimeConfiguration
from allms.cli.widgets.modal import ModalScreenWidget
from allms.core.state import GameStateManager


class BaseModalScreen(ModalScreen):
    """ Base class for a modal screen """

    def __init__(self,
                 title: str,
                 config: RunTimeConfiguration,
                 state_manager: GameStateManager,
                 widget_cls: Type[ModalScreenWidget],
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._title = title
        self._config = config
        self._state_manager = state_manager
        self._widget = widget_cls(self._title, self._config, self._state_manager)

    def compose(self) -> ComposeResult:
        yield self._widget
        yield Footer()

from typing import Type

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import ModalScreen
from textual.widgets import Footer

from allms.config import BindingConfiguration, RunTimeConfiguration
from allms.cli.widgets.modal import ModalScreenWidget
from allms.core.state import GameStateManager


class BaseModalScreen(ModalScreen):
    """ Base class for a modal screen """

    BINDINGS = [
        Binding(BindingConfiguration.modal_close_screen, "close_modal_screen", "Close", priority=True)
    ]

    def __init__(self,
                 title: str,
                 config: RunTimeConfiguration,
                 state_manager: GameStateManager,
                 widget_cls: Type[ModalScreenWidget],
                 widget_params: dict = None,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._title = title
        self._config = config
        self._state_manager = state_manager

        if widget_params is None:
            widget_params = dict()
        self._widget = widget_cls(self._title, self._config, self._state_manager, **widget_params)

    def compose(self) -> ComposeResult:
        yield self._widget
        yield Footer()

    def action_close_modal_screen(self) -> None:
        """ Invoked when key binding for closing the screen is pressed """
        self.app.pop_screen()

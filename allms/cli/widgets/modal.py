from textual.containers import Vertical

from allms.config import RunTimeConfiguration, StyleConfiguration
from allms.core.state import GameStateManager


class ModalScreenWidget(Vertical):
    """ Base class for a modal screen widget """

    def __init__(self, title: str, config: RunTimeConfiguration, state_manager: GameStateManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._title = title
        self._config = config
        self._state_manager = state_manager

    def on_mount(self) -> None:
        self.add_class(StyleConfiguration.class_border)
        self.add_class(StyleConfiguration.class_modal_container)

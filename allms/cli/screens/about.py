from allms.config import RunTimeConfiguration
from allms.cli.widgets.about import AboutAppWidget
from allms.core.state import GameStateManager
from .modal import BaseModalScreen


class AboutAppScreen(BaseModalScreen):
    """ Screen for displaying information about the app """

    def __init__(self, title: str, config: RunTimeConfiguration, state_manager: GameStateManager, *args, **kwargs):
        super().__init__(title, config, state_manager, AboutAppWidget, *args, **kwargs)

from allms.config import RunTimeConfiguration
from allms.cli.widgets.customize import CustomizeAgentsWidget
from allms.core.state import GameStateManager
from .modal import BaseModalScreen


class CustomizeAgentsScreen(BaseModalScreen):
    """ Screen for customizing the agents """

    def __init__(self, title: str, config: RunTimeConfiguration, state_manager: GameStateManager, *args, **kwargs):
        super().__init__(title, config, state_manager, CustomizeAgentsWidget, *args, **kwargs)

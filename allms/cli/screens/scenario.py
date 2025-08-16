from allms.config import RunTimeConfiguration
from allms.cli.widgets.scenario import ChatScenarioWidget
from allms.core.state import GameStateManager
from .modal import BaseModalScreen


class ChatScenarioScreen(BaseModalScreen):
    """ Screen for showing the current scenario """

    def __init__(self, title: str, config: RunTimeConfiguration, state_manager: GameStateManager, *args, **kwargs):
        super().__init__(title, config, state_manager, ChatScenarioWidget, *args, **kwargs)

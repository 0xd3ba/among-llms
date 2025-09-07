from allms.config import RunTimeConfiguration
from allms.cli.widgets.vote import VotingWidget
from allms.core.state import GameStateManager
from .modal import BaseModalScreen


class VotingScreen(BaseModalScreen):
    """ Screen for showing the current voting """

    def __init__(self, title: str, config: RunTimeConfiguration, state_manager: GameStateManager, *args, **kwargs):
        super().__init__(title, config, state_manager, VotingWidget, *args, **kwargs)

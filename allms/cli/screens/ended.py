from allms.config import RunTimeConfiguration
from allms.cli.widgets.ended import GameEndedWidget
from allms.core.state import GameStateManager
from .modal import BaseModalScreen


class GameEndedScreen(BaseModalScreen):
    """ Screen for notifying that the game has ended """

    def __init__(self, title: str, config: RunTimeConfiguration, state_manager: GameStateManager, *args, **kwargs):
        super().__init__(title, config, state_manager, GameEndedWidget, *args, **kwargs)

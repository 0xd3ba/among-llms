from allms.config import RunTimeConfiguration
from allms.cli.widgets.load import LoadGameStateWidget
from allms.core.state import GameStateManager
from .modal import BaseModalScreen


class LoadGameStateScreen(BaseModalScreen):
    """ Screen for notifying that the game has ended """

    def __init__(self, title: str, config: RunTimeConfiguration, state_manager: GameStateManager, *args, **kwargs):
        super().__init__(title, config, state_manager, LoadGameStateWidget, *args, **kwargs)

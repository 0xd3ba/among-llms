from allms.config import RunTimeConfiguration
from allms.cli.widgets.modify import ModifyMessageWidget
from allms.core.state import GameStateManager
from .modal import BaseModalScreen


class ModifyMessageScreen(BaseModalScreen):
    """ Screen for editing/deleting messages of the agents """

    def __init__(self, title: str, config: RunTimeConfiguration, state_manager: GameStateManager, *args, **kwargs):
        super().__init__(title, config, state_manager, ModifyMessageWidget, *args, **kwargs)

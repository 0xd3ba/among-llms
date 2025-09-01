from allms.config import RunTimeConfiguration
from allms.cli.widgets.exit import ChatExitWidget
from allms.core.state import GameStateManager
from .modal import BaseModalScreen


class ChatExitScreen(BaseModalScreen):
    """ Screen for exiting the chatroom """

    def __init__(self, title: str, config: RunTimeConfiguration, state_manager: GameStateManager, *args, **kwargs):
        super().__init__(title, config, state_manager, ChatExitWidget, *args, **kwargs)

from allms.config import RunTimeConfiguration
from allms.cli.widgets.new import NewChatroomWidget
from allms.core.state import GameStateManager
from .modal import BaseModalScreen


class NewChatScreen(BaseModalScreen):
    """ Screen for creating new chatroom """

    def __init__(self, title: str, config: RunTimeConfiguration, state_manager: GameStateManager, *args, **kwargs):
        super().__init__(title, config, state_manager, NewChatroomWidget, *args, **kwargs)

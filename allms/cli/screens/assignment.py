from allms.config import RunTimeConfiguration
from allms.cli.widgets.assignment import YourAgentAssignmentWidget
from allms.core.state import GameStateManager
from .modal import BaseModalScreen


class YourAgentAssignmentScreen(BaseModalScreen):
    """ Screen for notifying your random assignment """

    def __init__(self, title: str, config: RunTimeConfiguration, state_manager: GameStateManager, *args, **kwargs):
        super().__init__(title, config, state_manager, YourAgentAssignmentWidget, *args, **kwargs)

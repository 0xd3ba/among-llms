import copy
from typing import Optional

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import Label, TextArea, Select, Button

from allms.config import BindingConfiguration, RunTimeConfiguration
from allms.core.agents import AgentFactory
from allms.core.state import GameStateManager
from .modal import ModalScreenWidget


class YourAgentAssignmentWidget(ModalScreenWidget):

    def __init__(self, title: str, config: RunTimeConfiguration, state_manager: GameStateManager, *args, **kwargs):
        super().__init__(title, config, state_manager, *args, **kwargs)
        self._agent_id = self._state_manager.get_user_assigned_agent_id()
        self._agent = self._state_manager.get_agent(self._agent_id)
        self._agent_persona = self._agent.get_persona()

    def compose(self) -> ComposeResult:
        textbox = TextArea(text=self._agent_persona, show_line_numbers=True, read_only=True)
        with VerticalScroll():
            yield self._wrap_inside_container(textbox, Horizontal, border_title="Agent's Persona")

        textbox.focus()

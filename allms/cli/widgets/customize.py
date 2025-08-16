from typing import Optional

from textual import on
from textual.app import ComposeResult
from textual.binding import BindingsMap
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import Label, TextArea, Select, Button

from allms.config import BindingConfiguration, RunTimeConfiguration
from allms.core.agents import AgentFactory
from allms.core.state import GameStateManager
from .modal import ModalScreenWidget


class CustomizeAgentsWidget(ModalScreenWidget):

    BINDINGS = [
        (BindingConfiguration.new_chat_randomize_agent_persona, "randomize_agent_persona", "Randomize Agent Persona")
    ]

    def __init__(self, title: str, config: RunTimeConfiguration, state_manager: GameStateManager, read_only: bool = False, *args, **kwargs):
        super().__init__(title, config, state_manager, *args, **kwargs)
        self._read_only = read_only
        self._all_agents = self._state_manager.get_all_agents()
        self._agent_ids = sorted(list(self._all_agents.keys()), key=AgentFactory.agent_id_comparator)

        self._id_btn_confirm = "customize-agent-confirm-btn"
        self._id_btn_cancel = "customize-agent-cancel-btn"

        # Mapping between agent ID and newly edited persona
        self._edited_agents_personas: dict[str, str] = {}

        self._curr_agent_id_selected: str = ""
        self._persona_text_box: Optional[TextArea] = None

        # Unset the bindings to avoid editing in read-only mode
        if self._read_only:
            self._bindings = BindingsMap()

    def compose(self) -> ComposeResult:
        agent_ids = [(aid, aid) for aid in self._agent_ids]
        default_agent_id = self._agent_ids[0]
        default_text = self._all_agents[default_agent_id].persona

        select_box = Select(options=agent_ids, allow_blank=False, value=default_agent_id, compact=True)
        textbox = TextArea(text=default_text, show_line_numbers=True, read_only=self._read_only)
        confirm_btn = Button("Confirm", variant="success", id=self._id_btn_confirm, compact=True)
        cancel_btn = Button("Cancel", variant="error", id=self._id_btn_cancel, compact=True)

        with VerticalScroll():
            yield self._wrap_inside_container(select_box, Horizontal, border_title="Choose Agent")
            yield self._wrap_inside_container(textbox, Horizontal, border_title="Agent's Persona", cid="persona-textbox")

        # read-only mode happens when we are inside the chatroom and we need to see all the agent personas
        # Instead of creating a dedicated widget for it, re-use this widget -- bit of an ugly solution, but it gets the
        # job done ... for now atleast ¯\_(ツ)_/¯
        # Note: There is no need for the buttons in read-only mode
        if not self._read_only:
            yield self._wrap_inside_container([cancel_btn, Label(" "), confirm_btn], Horizontal, cid="customize-agent-buttons")

        select_box.focus()

        self._curr_agent_id_selected = default_agent_id
        self._persona_text_box = textbox

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """ Event handler for button clicked event """
        btn_pressed_id = event.button.id
        if btn_pressed_id == self._id_btn_cancel:
            pass  # Nothing needs to be done -- screen will be popped on either button press

        elif btn_pressed_id == self._id_btn_confirm:
            for (agent_id, new_persona) in self._edited_agents_personas.items():
                self._all_agents[agent_id].update_persona(new_persona)

        else:
            # Should not arrive at this branch or else there is a bug
            raise RuntimeError(f"Received a button pressed event from button-id({btn_pressed_id}) on {self.__class__.__name__}")

        self.app.pop_screen()

    @on(Select.Changed)
    async def handler_agent_id_changed(self, event: Select.Changed) -> None:
        """ Handler for handling events when number of agents is changed """
        agent_id = event.value
        self._persona_text_box.text = self._all_agents[agent_id].get_persona()
        self._curr_agent_id_selected = agent_id

    @on(TextArea.Changed)
    async def handler_agent_persona_changed(self, event: TextArea.Changed) -> None:
        """ Handler for handling events when agent's persona has changed """
        new_persona = event.text_area.text
        self._edited_agents_personas[self._curr_agent_id_selected] = new_persona

    def action_randomize_agent_persona(self) -> None:
        """ Invoked when key binding for randomizing agent persona is pressed """
        agent_id = self._curr_agent_id_selected
        persona = self._state_manager.generate_persona(agent_id, self._agent_ids)
        self._edited_agents_personas[self._curr_agent_id_selected] = persona

        self._persona_text_box.text = persona

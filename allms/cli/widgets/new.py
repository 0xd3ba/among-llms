from typing import Type, Optional

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import Label, TextArea, Select, Button

from allms.cli.screens.chat import ChatroomScreen
from allms.cli.screens.customize import CustomizeAgentsScreen
from allms.cli.widgets.modal import ModalScreenWidget
from allms.config import AppConfiguration, BindingConfiguration, RunTimeConfiguration, StyleConfiguration
from allms.core.state import GameStateManager


class NewChatroomWidget(ModalScreenWidget):

    BINDINGS = [
        Binding(BindingConfiguration.new_chat_randomize_scenario, "randomize_scenario", "Randomize Scenario", priority=True),
        Binding(BindingConfiguration.new_chat_customize_agents, "customize_agents", "Customize Agents")
    ]

    def __init__(self, title, config: RunTimeConfiguration, state_manager: GameStateManager, *args, **kwargs):
        super().__init__(title, config, state_manager, *args, **kwargs)

        min_agents = AppConfiguration.min_agent_count
        max_agents = self._config.max_agent_count
        genres = self._state_manager.get_available_genres()
        genres = sorted(list(genres))

        # Choices should be of following type: (value_displayed_in_UI, value_returned_on_selection)
        self._n_agents_choices = [(str(i), i) for i in range(min_agents, max_agents + 1)]
        self._genre_choices = [(g.title(), g) for g in genres]

        self._default_n_agents = self._config.default_agent_count

        self._id_n_agents_list = "new-chat-n-agents-list"
        self._id_genres_list = "new-chat-genres-list"
        self._id_btn_confirm = "new-chat-confirm"
        self._id_btn_cancel = "new-chat-cancel"

        self._new_scenario: Optional[str] = None
        self._scenario_textbox: Optional[TextArea] = None
        self._genres_list: Optional[Select] = None
        self._n_agents_list: Optional[Select] = None

    async def on_mount(self) -> None:
        await self._state_manager.new()   # Create a new game state
        default_genre = self._state_manager.get_genre()
        self._genres_list.value = default_genre
        self._scenario_textbox.text = self._state_manager.get_scenario()

    def compose(self) -> ComposeResult:

        scenario_textbox = TextArea(show_line_numbers=True)
        genres_list = Select(options=self._genre_choices, allow_blank=False, compact=True, id=self._id_genres_list)
        num_agents_list = Select(options=self._n_agents_choices, allow_blank=False, value=self._default_n_agents, compact=True, id=self._id_n_agents_list)
        confirm_btn, cancel_btn = self._create_confirm_cancel_buttons(self._id_btn_confirm, self._id_btn_cancel)

        scenario_textbox.focus()

        with VerticalScroll():
            yield self._wrap_inside_container(genres_list, Horizontal, border_title="Choose Genre")
            yield self._wrap_inside_container(scenario_textbox, Horizontal, border_title="Scenario", cid="scenario-textbox")
            yield self._wrap_inside_container(num_agents_list, Horizontal, border_title="No. of Agents")
        yield self._wrap_inside_container([cancel_btn, Label(" "), confirm_btn], Horizontal, cid="new-chat-buttons")

        # Save the references as they will be needed later on, for key bind actions etc.
        self._scenario_textbox = scenario_textbox
        self._genres_list = genres_list
        self._n_agents_list = num_agents_list

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """ Event handler for button clicked event """
        btn_pressed_id = event.button.id
        if btn_pressed_id == self._id_btn_cancel:
            self.app.pop_screen()

        elif btn_pressed_id == self._id_btn_confirm:
            if self._new_scenario is not None:
                self._state_manager.update_scenario(self._new_scenario)

            # Pick an agent ID at random and assign it to the user, then notify of the assignment
            your_agent_id = self._state_manager.pick_random_agent_id()
            self._state_manager.assign_agent_to_user(your_agent_id)

            self.app.pop_screen()
            self.app.push_screen(ChatroomScreen(self._config, self._state_manager))

        else:
            # Should not arrive at this branch or else there is a bug
            raise RuntimeError(f"Received a button pressed event from button-id({btn_pressed_id}) on {self.__class__.__name__}")

    @on(Select.Changed)
    async def handler_select_item_changed(self, event: Select.Changed) -> None:
        """ Handler for handling events when number of agents is changed """
        if event.select.id == self._id_n_agents_list:
            n_agents = event.value
            self._state_manager.create_agents(n_agents)

        elif event.select.id == self._id_genres_list:
            genre = event.value
            # On updating the genre, update the scenario and the agents
            self._state_manager.update_genre(genre)
            self.action_randomize_scenario()
            self._state_manager.create_agents(self._n_agents_list.value)

    @on(TextArea.Changed)
    async def handler_scenario_changed(self, event: TextArea.Changed) -> None:
        """ Handler for handling events when scenario has changed """
        self._new_scenario = event.text_area.text

    def action_randomize_scenario(self) -> None:
        """ Invoked when key binding for randomizing scenario is pressed """
        scenario = self._state_manager.generate_scenario()
        self._state_manager.update_scenario(scenario)
        self._scenario_textbox.text = scenario

    def action_customize_agents(self) -> None:
        """ Invoked when key binding for customizing agents is pressed """
        customize_screen = CustomizeAgentsScreen("Customize Agents", self._config, self._state_manager)
        self.app.push_screen(customize_screen)

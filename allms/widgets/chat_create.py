from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll, Container
from textual.widgets import Label, Button, Footer

from allms.config import AppConfiguration, StyleConfiguration
from .components.text_area import TextAreaComponent
from .components.radio_set import RadioSetComponent
from .components.selection import SelectComponent


class CreateNewChatWidget(Container):
    """ Class for the widget to display new chat settings """

    def __init__(self):
        super().__init__()
        self.border_title = "Create New Chatroom"

        self._button_id_customize_agents = "btn-customize-agents"
        self._button_id_chat_creation_cancel = "btn-cancel-chat-creation"
        self._button_id_chat_creation_confirm = "btn-confirm-chat-creation"

        ai_models = [model for (model, _) in AppConfiguration.ai_models]

        # Note: There needs to be atleast 2 agents to start the game and 3 agents (including yourself)
        # to make the game non-trivial
        max_agents = AppConfiguration.max_agents
        assert max_agents >= 3, f"Max. Agents should be atleast >= 3"
        n_agents_choices = [str(i) for i in range(3, max_agents+1)]
        def_n_agent_idx = n_agents_choices.index(str(AppConfiguration.default_n_agents))

        self._select_ai_model = RadioSetComponent(title="Choose AI Model", choices=ai_models)
        self._select_reasoning_lvl = RadioSetComponent(title="Reasoning Level", choices=AppConfiguration.ai_reasoning_levels)
        self._scenario_input = TextAreaComponent(title="Scenario")
        # Note: -1 because default_choice is the index to the choices list
        self._select_agents = SelectComponent(choices=n_agents_choices, default_choice=def_n_agent_idx)

    def on_mount(self) -> None:
        self.add_class(StyleConfiguration.css_class_round_border)

    def compose(self) -> ComposeResult:
        with Vertical(id="create-new-chat-vertical"):
            with VerticalScroll(id="create-chat-vertical-scroll"):

                with Horizontal(id="select-ai-model-reasoning"):
                    yield self._select_ai_model
                    yield self._select_reasoning_lvl

                yield self._scenario_input
                with Horizontal(classes=StyleConfiguration.css_class_round_border, id="select_num_agents_container") as select_agent_container:
                    select_agent_container.border_title = "No. of Agents"
                    select_agent_container.add_class(StyleConfiguration.css_class_highlight_border_on_focus)

                    yield self._select_agents
                    yield Button("Customize", variant="primary", id=self._button_id_customize_agents)

            with Horizontal(id="confirm-chat-creation-buttons"):
                yield Button("Cancel", variant="error", id=self._button_id_chat_creation_cancel)
                yield Button("Confirm", variant="primary", id=self._button_id_chat_creation_confirm)

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == self._button_id_chat_creation_cancel:
            self.app.pop_screen()

        elif button_id == self._button_id_chat_creation_confirm:
            # TODO: Write the code to save the parameters and start the chat
            pass

        elif button_id == self._button_id_customize_agents:
            # TODO: Write the code to launch a new modal dialog to customize the agents
            pass

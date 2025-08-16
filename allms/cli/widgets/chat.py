from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Input, Label, Select, TextArea

from allms.cli.screens.assignment import YourAgentAssignmentScreen
from allms.config import BindingConfiguration, RunTimeConfiguration
from allms.core.state import GameStateManager


class ChatroomContents(VerticalScroll):
    """ Class for storing the contents of the chat """
    def __init__(self, config: RunTimeConfiguration, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._config = config

    def compose(self) -> ComposeResult:
        # TODO: Populate this with chat data
        yield Label()


class ChatroomIsTyping(Horizontal):
    """ Class for displaying typing status of agents """
    def compose(self) -> ComposeResult:
        # TODO: Implement this later on
        yield Label("Someone is typing ...")


class ChatroomWidget(Vertical):
    """ Class for the main chatroom widget """

    BINDINGS = [
        Binding(BindingConfiguration.chatroom_show_your_persona, "view_persona", "View your persona")
    ]

    def __init__(self, config: RunTimeConfiguration, state_manager: GameStateManager, is_disabled: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._config = config
        self._state_manager = state_manager
        self._is_disabled = is_disabled
        self._contents_widget = ChatroomContents(self._config)
        self._is_typing_widget = ChatroomIsTyping()

        self._id_btn_send = "chat-msg-send-btn"
        self._id_txt_area = "chat-msg-text-area"

        choices_send_to_tooltip = "Send to everyone or send a DM to a specific agent"
        choices_send_as_tooltip = "Send as you or masquerade as a different agent"

        # TODO: Set these dynamically from the chat data
        # Note: We assume the first item to be the default, so ensure it is set to the correct value
        self._choices_send_to = ["/all"]
        self._choices_send_as = ["You"]

        self._send_to_list = self.__create_choices(self._choices_send_to, widget_id="chat-send-to-options", tooltip=choices_send_to_tooltip)
        self._send_as_list = self.__create_choices(self._choices_send_as, widget_id="chat-send-as-options", tooltip=choices_send_as_tooltip)
        self._btn_send = Button("Send", variant="success", id=self._id_btn_send, disabled=is_disabled)

        placeholder_text = "Type your message ..."
        self._input_area = Input(placeholder=placeholder_text, id=self._id_txt_area, disabled=is_disabled)
        self._input_area.styles.min_width = len(placeholder_text) + 10

    def on_show(self) -> None:
        # Pick an agent ID at random and assign it to the user, then notify of the assignment
        your_agent_id = self._state_manager.pick_random_agent_id()
        self._state_manager.assign_agent_to_user(your_agent_id)
        self.__show_assignment_screen()

    def compose(self) -> ComposeResult:
        yield self._contents_widget
        yield self._is_typing_widget
        with Horizontal(id="chat-type-send-container"):
            yield self._send_to_list
            yield self._input_area
            yield self._send_as_list
            yield self._btn_send

        if not self._is_disabled:
            self._input_area.focus()

    def __create_choices(self, choices: list[str], widget_id: str = "", tooltip: str = "") -> Select:
        """ Helper method to create a choices list and return it """
        assert len(choices) > 0, f"Expected number of choices for widget-id({widget_id}) in {self.__class__} " + \
                                 "to be > 0 but received an empty list"

        choices_fmt = [(c, c) for c in choices]
        default_choice = choices[0]

        widget = Select(options=choices_fmt, allow_blank=False, value=default_choice, tooltip=tooltip)
        if widget_id:
            widget.id = widget_id

        return widget

    def __show_assignment_screen(self) -> None:
        """ Helper method to show the assignment screen """
        your_agent_id = self._state_manager.get_user_assigned_agent_id()
        screen_title = f"You are {your_agent_id}"
        self.app.push_screen(YourAgentAssignmentScreen(screen_title, self._config, self._state_manager))

    def action_view_persona(self) -> None:
        """ Invoked when key binding for viewing your persona is pressed """
        self.__show_assignment_screen()

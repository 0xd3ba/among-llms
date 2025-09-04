import asyncio
from typing import Optional

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Input, Select, Static
from textual.worker import Worker

from allms.cli.callbacks import ChatCallbackType, ChatCallbacks
from allms.cli.screens.assignment import YourAgentAssignmentScreen
from allms.cli.screens.customize import CustomizeAgentsScreen
from allms.cli.screens.ended import GameEndedScreen
from allms.cli.screens.exit import ChatExitScreen
from allms.cli.screens.modify import ModifyMessageScreen
from allms.cli.screens.scenario import ChatScenarioScreen
from allms.cli.screens.vote import VotingScreen
from allms.cli.widgets.input import MessageBox
from allms.cli.widgets.clock import ChatClock
from allms.cli.widgets.contents import ChatroomContentsWidget
from allms.cli.widgets.type import ChatroomIsTyping
from allms.config import BindingConfiguration, RunTimeConfiguration, ToastConfiguration
from allms.core.state import GameStateManager


class ChatroomWidget(Vertical):
    """ Class for the main chatroom widget """

    BINDINGS = [
        Binding(BindingConfiguration.chatroom_show_scenario, "view_scenario", "Scenario"),
        Binding(BindingConfiguration.chatroom_show_your_persona, "view_persona", "Your Persona"),
        Binding(BindingConfiguration.chatroom_show_all_persona, "view_all_personas", "All Personas"),
        Binding(BindingConfiguration.chatroom_modify_msgs, "modify_msgs", "Modify Messages"),
        Binding(BindingConfiguration.chatroom_start_vote, "start_a_vote", "Vote"),
        Binding(BindingConfiguration.chatroom_quit, "chatroom_quit", "Quit", priority=True)
    ]

    def __init__(self, config: RunTimeConfiguration, state_manager: GameStateManager, is_disabled: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._config = config
        self._state_manager = state_manager
        self._is_disabled = is_disabled
        self._your_agent_id = self._state_manager.get_user_assigned_agent_id()
        self._game_ended = self._state_manager.get_game_ended()

        self._prefix_send_to = "->"
        self._prefix_send_as = ""
        self._id_send_to_all = "All"
        self._id_send_as_you = f"{self._your_agent_id} (You)"

        self._remaining_agents_widget = Static(id="chat-remaining-agents-widget")

        self._contents_widget = ChatroomContentsWidget(self._config, self._state_manager, display_you_as=self._id_send_as_you)
        self._is_typing_widget = ChatroomIsTyping()

        self._id_btn_send = "chat-msg-send-btn"
        self._id_txt_area = "chat-msg-text-area"
        self._id_send_to_list = "chat-send-to-options"
        self._id_send_as_list = "chat-send-as-options"

        choices_send_to_tooltip = "Send to everyone or send a DM to a specific agent"
        choices_send_as_tooltip = "Send as you or masquerade as a different agent"

        # Populate the send-to and send-as selection lists
        # Note: We assume the first item to be the default, so ensure it is set to the correct value
        self._choices_send_to = []
        self._choices_send_as = []
        self.__add_agents_to_selection_list(self._choices_send_to, first_item=self._id_send_to_all, prefix=self._prefix_send_to)
        self.__add_agents_to_selection_list(self._choices_send_as, first_item=self._id_send_as_you, prefix=self._prefix_send_as)

        self._send_to_list = self.__create_choices(self._choices_send_to, widget_id=self._id_send_to_list, tooltip=choices_send_to_tooltip)
        self._send_as_list = self.__create_choices(self._choices_send_as, widget_id=self._id_send_as_list, tooltip=choices_send_as_tooltip)
        self._btn_send = Button("Send", variant="success", id=self._id_btn_send, disabled=is_disabled)

        placeholder_text = "Type your message ..."
        self._input_area = MessageBox(on_send_callback=self.action_send_message, placeholder=placeholder_text, id=self._id_txt_area, disabled=is_disabled)
        self._input_area.styles.min_width = len(placeholder_text) + 10

        # Stores the user typed message and send-as/send-to items
        self._current_msg: str = ""
        self._current_send_as: str = ""
        self._current_send_to: str = ""

        # Finally, register the callback for updating the new chat messages
        self._self_callbacks = ChatCallbacks(self.__generate_callbacks())
        self._state_manager.register_chat_callbacks(self._self_callbacks)
        self._chat_worker: Optional[Worker] = None
        self._background_worker: Optional[Worker] = None

    def on_show(self) -> None:
        # Show what the agent the user has been assigned
        if not self._is_disabled:
            self.__show_assignment_screen()
            worker_group = "chat-loop"
            self._chat_worker = self.run_worker(self._state_manager.start_llms(), group=worker_group, exclusive=True)
            self._background_worker = self.run_worker(self._state_manager.background_worker(), group=worker_group, exclusive=True)
        else:
            self.__send_notification(
                title="Game has Already Ended",
                message="The game has already ended. You can browse through the chats or export them"
            )

    def compose(self) -> ComposeResult:
        self.__update_remaining_agent_counts()
        with Horizontal(id="chat-header-container"):
            yield self._remaining_agents_widget
            yield ChatClock()

        yield self._contents_widget
        yield self._is_typing_widget

        with Horizontal(id="chat-type-send-container"):
            yield self._send_to_list
            yield self._input_area
            yield self._send_as_list
            yield self._btn_send

        if not self._is_disabled:
            self._input_area.focus()
        else:
            self._contents_widget.focus()

    def __create_choices(self, choices: list[tuple[str, str]], widget_id: str = "", tooltip: str = "") -> Select:
        """ Helper method to create a choices list and return it """
        assert len(choices) > 0, f"Expected number of choices for widget-id({widget_id}) in {self.__class__} " + \
                                 "to be > 0 but received an empty list"

        default_choice = choices[0][1]

        widget = Select(options=choices, allow_blank=False, value=default_choice, tooltip=tooltip)
        if widget_id:
            widget.id = widget_id

        return widget

    def __show_assignment_screen(self) -> None:
        """ Helper method to show the assignment screen """
        your_agent_id = self._state_manager.get_user_assigned_agent_id()
        screen_title = f"You are {your_agent_id}"
        self.app.push_screen(YourAgentAssignmentScreen(screen_title, self._config, self._state_manager))

    def __add_agents_to_selection_list(self, choices_list: list[tuple[str, str]], first_item: str, prefix: str) -> None:
        """ Helper method to add agent selection choices to the given list """
        choices_list.clear()  # Need to do this to ensure when an agent is kicked out, it is reflected in the choices
        agent_ids = self._state_manager.get_all_remaining_agents_ids()
        your_agent_id = self._state_manager.get_user_assigned_agent_id()

        for aid in [first_item] + agent_ids:
            if aid == your_agent_id:
                continue
            item = (f"{prefix} {aid}", aid)
            choices_list.append(item)

    def __update_remaining_agent_counts(self) -> None:
        """ Helper method to update the remaining agents text widget """
        n_remaining = len(self._state_manager.get_all_remaining_agents_ids()) - 1  # Ignore yourself
        n_terminated = len(self._state_manager.get_all_agents()) - n_remaining - 1

        text = f"Remaining: [b]{n_remaining}[/]; Terminated: [b]{n_terminated}[/]"
        self._remaining_agents_widget.update(text)

    def __generate_callbacks(self) -> dict:
        """ Generates the callback mapping and returns it """
        callback_map = {
            ChatCallbackType.NEW_MESSAGE_RECEIVED: self.__update_new_chat_message,
            ChatCallbackType.UPDATE_AGENTS_LIST: self.__update_agents_list,
            ChatCallbackType.IS_TYPING: self.__is_typing,
            ChatCallbackType.ANNOUNCE_EVENT: self.__event_occurred,
            ChatCallbackType.NOTIFY_TOAST: self.__send_notification,
            ChatCallbackType.TERMINATE_ALL_TASKS: self.__cancel_all_bg_tasks,
            ChatCallbackType.GAME_HAS_ENDED: self.__game_has_officially_ended,
            ChatCallbackType.CLOSE_CHATROOM: self.__close_chatroom
        }

        return callback_map

    def __update_new_chat_message(self, msg_id: str) -> None:
        """ Callback method to display the message with the given ID to the widget """
        # Note: Do not call this method directly, instead use the state manager to invoke this callback
        self._contents_widget.add_new_message(msg_id)

    def __is_typing(self, agent_id: str, is_typing: bool) -> None:
        """ Callback method to update the current agents typing """
        if is_typing:
            self._is_typing_widget.add_typing(agent_id)
        else:
            self._is_typing_widget.remove_typing(agent_id)

    def __event_occurred(self, event: str) -> None:
        """ Callback method to display the event on the screen """
        self._contents_widget.announce_event(event)

    def __send_notification(self, title: str, message: str, severity: str = ToastConfiguration.type_information) -> None:
        """ Callback method to send a notification toast """
        self.notify(title=title, message=message, severity=severity)

    def __cancel_all_bg_tasks(self) -> None:
        """ Callback method to cancel all the background tasks and disable the inputs """
        self._state_manager.stop_llms()
        self._chat_worker and self._chat_worker.cancel()
        self._background_worker and self._background_worker.cancel()
        self._game_ended = True

        # Disable all the inputs since this is only called on game termination
        self._send_to_list.disabled = True
        self._input_area.disabled = True
        self._send_as_list.disabled = True
        self._btn_send.disabled = True

        self._contents_widget.focus()

    def __game_has_officially_ended(self, conclusion: str) -> None:
        """ Callback method to display the game ended screen """
        self._game_ended = True
        screen = GameEndedScreen(title=conclusion, config=self._config, state_manager=self._state_manager)
        self.app.push_screen(screen)

    def __update_agents_list(self) -> None:
        """ Callback method to update the remaining agents from the lists """
        self.__add_agents_to_selection_list(self._choices_send_to, first_item=self._id_send_to_all, prefix=self._prefix_send_to)
        self.__add_agents_to_selection_list(self._choices_send_as, first_item=self._id_send_as_you, prefix=self._prefix_send_as)

        self._send_to_list.set_options(self._choices_send_to)
        self._send_as_list.set_options(self._choices_send_as)

        self.__update_remaining_agent_counts()

    def __close_chatroom(self) -> None:
        """ Callback method to close the chatroom """
        self.__cancel_all_bg_tasks()
        self.app.pop_screen()

    @on(Input.Changed)
    def handler_user_text_message_changed(self, event: Input.Changed) -> None:
        """ Handler invoked when there is a change in message box """
        input_text = event.input.value
        self._current_msg = input_text

    @on(Select.Changed)
    def handler_select_item_changed(self, event: Select.Changed) -> None:
        """ Handler invoked when there is a change in the select item for either of the choices list """
        select_widget = event.select
        if select_widget.id == self._id_send_as_list:
            self._current_send_as = self._send_as_list.value
        elif select_widget.id == self._id_send_to_list:
            self._current_send_to = self._send_to_list.value
        else:
            # Should not arrive at this branch or else there is a bug
            raise RuntimeError(f"Received unexpected id({select_widget.id}) on selection list handler")

    @on(Button.Pressed)
    def handler_send_button_clicked(self, event: Button.Pressed) -> None:
        """ Handler invoked when send button is clicked """
        btn_id = event.button.id
        if btn_id == self._id_btn_send:
            self.action_send_message()
        else:
            # Should not come to this branch or else there is a bug
            raise RuntimeError(f"What button with id={btn_id} did you click in the screen")

    def action_view_scenario(self) -> None:
        """ Invoked when key binding for viewing the scenario is pressed """
        screen_title = "Scenario"
        screen = ChatScenarioScreen(screen_title, self._config, self._state_manager)
        self.app.push_screen(screen)

    def action_view_persona(self) -> None:
        """ Invoked when key binding for viewing your persona is pressed """
        self.__show_assignment_screen()

    def action_view_all_personas(self) -> None:
        """ Invoked when key binding for viewing all personas is pressed """
        # Re-use customize agent screen but make it read-only
        screen_title = "Agent Personas"
        screen = CustomizeAgentsScreen(screen_title, self._config, self._state_manager, widget_params=dict(read_only=True))
        self.app.push_screen(screen)

    def action_send_message(self) -> None:
        """ Invoked when key binding for sending a message is pressed """
        current_msg = self._current_msg
        if len(current_msg) == 0:
            return

        # Prepare the constants required by state manager
        # Update the send-to / send-as before sending them to the state manager
        send_to = self._current_send_to
        send_to = None if (send_to == self._id_send_to_all) else send_to

        send_as = self._current_send_as
        send_as = self._your_agent_id if (send_as == self._id_send_as_you) else send_as

        # Doesn't matter if you're masquerading as a different agent or sending via your assigned agent ID
        # This handler is only executed when you type a message in the input box and send it -- i.e. sent by you
        sent_by_you = True

        async def _send():
            """ Asynchronous helper method to send the message """
            msg_id = await self._state_manager.send_message(msg=current_msg, sent_by=send_as, sent_to=send_to, sent_by_you=sent_by_you)
            await self._state_manager.on_new_message_received(msg_id)

        asyncio.gather(_send())
        # TODO: What if the user is replying to an older message? I guess the chat-contents class should take care of this

        # Finally reset the current text
        self._current_msg = ""
        self._input_area.value = ""

    def action_modify_msgs(self) -> None:
        """ Invoked when key binding for modifying messages is pressed """
        if self._game_ended:
            self.__send_notification(title="Can't Modify Messages", message="The game has already ended", severity=ToastConfiguration.type_error)
            return

        screen_title = "Modify Messages"
        screen = ModifyMessageScreen(screen_title, self._config, self._state_manager,
                                     widget_params=dict(chat_msg_edit_callback=self._contents_widget.edit_message,
                                                        chat_msg_delete_callback=self._contents_widget.delete_message))
        self.app.push_screen(screen)

    def action_chatroom_quit(self) -> None:
        """ Invoked when key binding for quitting the chatroom is pressed """
        title = "Exit Chatroom ?"
        screen = ChatExitScreen(title=title, config=self._config, state_manager=self._state_manager,
                                widget_params=dict(callbacks=self._self_callbacks))
        self.app.push_screen(screen)

    def action_start_a_vote(self) -> None:
        """ Invoked when key binding for starting a vote is pressed """
        if self._game_ended:
            self.__send_notification(title="Can't Vote", message="The game has already ended", severity=ToastConfiguration.type_error)
            return

        voting_in_progress, _ = self._state_manager.voting_has_started()
        screen_title = "Voting in Progress" if voting_in_progress else "Start a Vote"
        screen = VotingScreen(screen_title, self._config, self._state_manager)
        self.app.push_screen(screen)

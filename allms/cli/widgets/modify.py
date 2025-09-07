import asyncio
from typing import Callable, Optional, Type

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Label, TextArea, Select, Button, OptionList

from allms.config import AppConfiguration, BindingConfiguration, RunTimeConfiguration
from allms.core.agents import AgentFactory
from allms.core.chat import ChatMessage
from allms.core.state import GameStateManager
from .messages import ModifyMessageOptionListWidget
from .modal import ModalScreenWidget


class ModifyMessageWidget(ModalScreenWidget):

    BINDINGS = [
        Binding(BindingConfiguration.modify_msgs_mark_unmark_delete, "mark_unmark_delete_msg", "Mark/Unmark for Deletion", priority=True),
    ]

    def __init__(self,
                 title: str,
                 config: RunTimeConfiguration,
                 state_manager: GameStateManager,
                 chat_msg_edit_callback: Type[Callable],
                 chat_msg_delete_callback: Type[Callable],
                 *args, **kwargs):
        super().__init__(title, config, state_manager, *args, **kwargs)
        self._chat_msg_edit_callback = chat_msg_edit_callback
        self._chat_msg_delete_callback = chat_msg_delete_callback
        self._all_agents = self._state_manager.get_all_agents()
        self._agent_ids = sorted(list(self._all_agents.keys()), key=AgentFactory.agent_id_comparator)

        self._id_btn_confirm = "modify-msg-confirm-btn"
        self._id_btn_cancel = "modify-msg-cancel-btn"

        self._edited_msgs_map: dict[str, str] = {}  # Mapping between msg id and new/current msg content
        self._delete_msgs_set: set[str] = set()  # Set of msg ids to be deleted
        self._msgs_options_list = ModifyMessageOptionListWidget(self._config,
                                                                self._state_manager,
                                                                self._edited_msgs_map,
                                                                self._delete_msgs_set,
                                                                item_selected_callback=self.__on_message_option_item_changed)
        self._msg_text_box = TextArea()

        self._curr_agent_id_selected: str = ""
        self._curr_msg_selected: Optional[ChatMessage] = None

    def compose(self) -> ComposeResult:
        agent_ids = [(aid, aid) for aid in self._agent_ids]
        default_agent_id = self._agent_ids[0]
        self._msgs_options_list.on_agent_changed(default_agent_id)

        select_box = Select(options=agent_ids, allow_blank=False, value=default_agent_id, compact=True)
        confirm_btn, cancel_btn = self._create_confirm_cancel_buttons(self._id_btn_confirm, self._id_btn_cancel)
        textbox = self._msg_text_box

        with VerticalScroll(id="modify-msg-vertical-scroll"):
            with Horizontal(id="modify-msg-parent-container"):
                with Vertical(id="modify-msg-select-options-container"):
                    yield self._wrap_inside_container(select_box, Horizontal, border_title="Choose Agent")
                    yield self._wrap_inside_container(self._msgs_options_list, Horizontal, border_title="Choose Message", cid="choose-msg-list")
                yield self._wrap_inside_container(textbox, Horizontal, border_title="Message", cid="modify-msg-textbox")

        yield self._wrap_inside_container([cancel_btn, Label(" "), confirm_btn], Horizontal, cid="modify-msg-buttons")

        select_box.focus()
        self._curr_agent_id_selected = default_agent_id

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """ Event handler for button clicked event """
        btn_pressed_id = event.button.id
        if btn_pressed_id == self._id_btn_cancel:
            pass  # Nothing needs to be done -- screen will be popped on either button press

        elif btn_pressed_id == self._id_btn_confirm:
            # Edit the widgets on the screen to reflect the edited messages
            # Note: First need to update the messages state before invoking the callback
            async def _modify_message(state_callback: Type[Callable], ui_callback: Type[Callable], mid: str, *args, **kwargs):
                """ Asynchronous helper method to modify the state and UI for edit/delete messages """
                await state_callback(mid, *args, **kwargs)
                await ui_callback(mid)

            edit_coroutines = []
            for (msg_id, msg_contents) in self._edited_msgs_map.items():
                assert msg_id not in self._delete_msgs_set, f"Trying to edit a message({msg_id} that has been " + \
                    f"marked for deletion -- This should not happen."
                edit_coroutines.append(_modify_message(self._state_manager.edit_message, self._chat_msg_edit_callback, msg_id, msg_contents, edited_by_you=True))

            # Now delete the messages in the delete set
            delete_coroutines = [_modify_message(self._state_manager.delete_message, self._chat_msg_delete_callback, mid, deleted_by_you=True)
                                 for mid in self._delete_msgs_set]

            asyncio.gather(*edit_coroutines, *delete_coroutines)

        else:
            # Should not arrive at this branch or else there is a bug
            raise RuntimeError(f"Received a button pressed event from button-id({btn_pressed_id}) on {self.__class__.__name__}")

        self.app.pop_screen()

    def action_mark_unmark_delete_msg(self) -> None:
        """ Invoked when key binding for marking/unmarking a message for deletion is pressed """
        curr_msg = self._curr_msg_selected
        if curr_msg is None:
            return  # Ignore if no message is currently selected

        # If the message was already deleted previously -- nothing needs to be done
        if curr_msg.deleted:
            return

        if curr_msg.id in self._delete_msgs_set:
            self._delete_msgs_set.remove(curr_msg.id)
            self._msg_text_box.read_only = False
        else:
            self._delete_msgs_set.add(curr_msg.id)
            self._msg_text_box.read_only = True
            # If the message was being edited, discard the changes
            if curr_msg.id in self._edited_msgs_map:
                del self._edited_msgs_map[curr_msg.id]
                self._msg_text_box.text = curr_msg.msg

        self._msgs_options_list.on_message_content_changed(curr_msg.msg)

    def __on_message_option_item_changed(self, agent_msg: ChatMessage = None) -> None:
        """ Handler invoked when a different message item is selected"""
        self._curr_msg_selected = agent_msg
        text = ""
        read_only = True
        can_focus = False

        if self._curr_msg_selected is not None:
            text = self._curr_msg_selected.msg
            msg_id = self._curr_msg_selected.id

            if msg_id not in self._delete_msgs_set:
                if msg_id in self._edited_msgs_map:
                    text = self._edited_msgs_map[msg_id]
                read_only = False
                can_focus = True
            else:
                read_only = True

            # Overwrite everything if message was deleted
            if self._curr_msg_selected.deleted:
                read_only = True
                can_focus = False
                text = self._curr_msg_selected.msg

        self._msg_text_box.can_focus = can_focus
        self._msg_text_box.text = text
        self._msg_text_box.read_only = read_only

    @on(Select.Changed)
    async def handler_agent_id_changed(self, event: Select.Changed) -> None:
        """ Handler for handling events when agent is changed """
        agent_id = event.value
        self._msgs_options_list.on_agent_changed(agent_id)

    @on(TextArea.Changed)
    async def handler_agent_message_edited(self, event: TextArea.Changed) -> None:
        """ Handler for handling events when agent's message has been edited """
        new_msg = event.text_area.text
        if self._curr_msg_selected is None:
            return

        if new_msg == self._curr_msg_selected.msg:
            if self._curr_msg_selected.id in self._edited_msgs_map:
                del self._edited_msgs_map[self._curr_msg_selected.id]
        else:
            self._edited_msgs_map[self._curr_msg_selected.id] = new_msg

        # Note: Need to call the handler either ways as the display text needs to be reset
        self._msgs_options_list.on_message_content_changed(new_msg)

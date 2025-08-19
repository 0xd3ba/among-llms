from typing import Optional

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Label, Static

from allms.config import StyleConfiguration, RunTimeConfiguration
from allms.core.state import GameStateManager
from allms.core.chat import ChatMessage


class ChatBubbleWidget(Vertical):
    """ Class for a widget hosting a single message """
    def __init__(self, message: ChatMessage, state_manager: GameStateManager, your_message: bool, sent_by: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._message = message
        self._state_manager = state_manager
        self._your_message = your_message
        self._sent_by = sent_by
        self._chat_bubble: Optional[Static] = None

        self._css_id_your_message = "chat-bubble-you"
        self._css_id_other_message = "chat-bubble-other"

        # Set alignment based on the originator of the message -- if it was you (from your assigned agent), then
        # right-alignment otherwise left-alignment
        bubble_alignment = "right" if self._your_message else "left"
        self.styles.align = bubble_alignment, "middle"

    def compose(self) -> ComposeResult:
        msg_txt = self._message.msg
        title, subtitle = self.__create_border_title_subtitle()

        self._chat_bubble = Static(msg_txt)
        self._chat_bubble.add_class(StyleConfiguration.class_border)
        self.__add_border_text(title, subtitle)

        yield self._chat_bubble

    def edit_contents(self) -> None:
        """ Edits the contents of the chat bubble with the new contents """
        self._chat_bubble.update(self._message.msg)
        title, subtitle = self.__create_border_title_subtitle()
        self.__add_border_text(title, subtitle)

    def delete_contents(self) -> None:
        """ Deletes the contents of the chat bubble """
        new_content = "[i]This message has been deleted[/]"
        self._chat_bubble.update(new_content)
        title, subtitle = self.__create_border_title_subtitle()
        self.__add_border_text(title, subtitle)

    def __add_border_text(self, title: str, subtitle: str) -> None:
        """ Helper method to add border title and subtitle to the chat bubble """
        if self._chat_bubble is not None:
            self._chat_bubble.border_title = title
            self._chat_bubble.border_subtitle = subtitle

    def __create_border_title_subtitle(self) -> tuple[str, str]:
        """ Helper method to create the border text and returns it """
        msg_time = self._message.timestamp
        sent_by = self._sent_by
        sent_to = self._message.sent_to
        sent_by_you = self._message.sent_by_you
        edited = self._message.edited
        edited_by_you = self._message.edited_by_you
        deleted = self._message.deleted
        deleted_by_you = self._message.deleted_by_you

        title_suffix = "/[i]hacked[/]" if sent_by_you and (not self._your_message) else ""
        if sent_to is not None:
            title_suffix += f" -> {sent_to}"

        edited_text = ""
        if edited:
            by_you_text = " by you" if (edited_by_you and not self._your_message) else ""
            edited_text = f"[i](edited{by_you_text})[/]"
        if deleted:
            by_you_text = " by you" if (deleted_by_you and not self._your_message) else ""
            edited_text = f"[i](deleted{by_you_text})[/]"

        border_title = f"{sent_by}{title_suffix} {edited_text}"
        border_subtitle = f"{msg_time}"

        return border_title, border_subtitle


class ChatroomContentsWidget(VerticalScroll):
    """ Class for storing the contents of the chat """

    def __init__(self, config: RunTimeConfiguration, state_manager: GameStateManager, display_you_as: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._config = config
        self._state_manager = state_manager
        self._your_agent_id = self._state_manager.get_user_assigned_agent_id()
        self._display_you_as = display_you_as

        # Mapping between a message ID, and it's corresponding chat-bubble widget
        self._msg_map: dict[str, ChatBubbleWidget] = {}

    def compose(self) -> ComposeResult:
        return []  # TODO: Implement this to include initial widgets to the screen

    def add_new_message(self, msg_id: str) -> None:
        """ Method to add a new chat message to the widget """
        msg = self._state_manager.get_message(msg_id)
        your_msg = (msg.sent_by == self._your_agent_id)
        sent_by = msg.sent_by
        if your_msg:  # If sending as yourself, update the display name to reflect it
            sent_by = self._display_you_as

        msg_widget = ChatBubbleWidget(msg, self._state_manager, your_message=your_msg, sent_by=sent_by)
        self._msg_map[msg_id] = msg_widget

        self.mount(msg_widget)
        self.scroll_end(animate=False)

    def edit_message(self, msg_id: str) -> None:
        """ Method to edit an existing chat message """
        msg_widget = self._msg_map[msg_id]
        msg_widget.edit_contents()

    def delete_message(self, msg_id: str) -> None:
        """ Method to delete an existing chat message """
        msg_widget = self._msg_map[msg_id]
        msg_widget.delete_contents()

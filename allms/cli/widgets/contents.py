from typing import Optional

from textual.app import ComposeResult
from textual.containers import Container, Vertical, VerticalScroll
from textual.widget import Widget
from textual.widgets import Label, Static

from allms.config import StyleConfiguration, RunTimeConfiguration
from allms.core.state import GameStateManager
from allms.core.chat import ChatMessage


class ChatBubbleWidget(Container):
    """ Class for a widget hosting a single message """
    def __init__(self,
                 config: RunTimeConfiguration,
                 message: ChatMessage,
                 state_manager: GameStateManager,
                 your_message: bool,
                 sent_by: str,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._config = config
        self._message = message
        self._state_manager = state_manager
        self._your_message = your_message
        self._sent_by = sent_by
        self._container = Vertical()
        self._chat_bubble: Optional[Static] = None
        self._extra_bubble: Optional[Static] = None

        self._css_id_your_message = "chat-bubble-you"
        self._css_id_other_message = "chat-bubble-other"

        # Set alignment based on the originator of the message -- if it was you (from your assigned agent), then
        # right-alignment otherwise left-alignment
        bubble_alignment = "right" if self._your_message else "left"
        self.styles.align = bubble_alignment, "middle"

    def compose(self) -> ComposeResult:
        msg_txt = self._message.msg
        extra_txt = ""
        thought_process = self._message.thought_process
        suspect = "-"
        suspect_confidence = "-"
        suspect_reason = "-"

        with self._container:
            if self._message.suspect is not None:
                suspect = self._message.suspect
                suspect_confidence = self._message.suspect_confidence
                suspect_reason = self._message.suspect_reason

            if self._config.show_thought_process and not self._your_message:
                extra_txt = f"[italic dim]([b]Intent[/]: {thought_process})[/]"

            # Show suspects only if config allows, it was not sent by you and the message contains a suspect
            if self._config.show_suspects and not self._your_message and (self._message.suspect is not None):
                suspect_txt = f"[dim][b]Suspect[/]:    {suspect}[/]\n" + \
                              f"[dim][b]Confidence[/]: {suspect_confidence}[/]\n" + \
                              f"[dim][b]Reason[/]:     {suspect_reason}[/]\n"
                extra_txt = f"{extra_txt}\n\n{suspect_txt}"

            self._chat_bubble = Static(msg_txt)
            self._extra_bubble = Static(extra_txt)

            title, subtitle = self.__create_border_title_subtitle()
            self._container.add_class(StyleConfiguration.class_border)
            self.__add_border_text(title, subtitle, self._container)

            yield self._chat_bubble
            if not self._message.sent_by_you:
                yield self._extra_bubble
        yield self._container

    def edit_contents(self) -> None:
        """ Edits the contents of the chat bubble with the new contents """
        self._chat_bubble.update(self._message.msg)
        title, subtitle = self.__create_border_title_subtitle()
        self.__add_border_text(title, subtitle, self._container)

    def delete_contents(self) -> None:
        """ Deletes the contents of the chat bubble """
        new_content = f"[i]{self._message.msg}[/]"  # Already must have been updated by the state manager
        self._chat_bubble.update(new_content)
        title, subtitle = self.__create_border_title_subtitle()
        self.__add_border_text(title, subtitle)

    @staticmethod
    def __add_border_text(title: str, subtitle: str, widget: Container | Widget) -> None:
        """ Helper method to add border title and subtitle to the chat bubble """
        widget.border_title = title
        widget.border_subtitle = subtitle

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

        self._css_class_announcement_widget = "chatroom-announcement-widget"
        self._css_class_announcement_container = "chatroom-announcement-container"

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

        msg_widget = ChatBubbleWidget(self._config, msg, self._state_manager, your_message=your_msg, sent_by=sent_by)
        self._msg_map[msg_id] = msg_widget
        self.__add_widget_to_screen(msg_widget)

    async def edit_message(self, msg_id: str) -> None:
        """ Method to edit an existing chat message """
        msg_widget = self._msg_map[msg_id]
        msg_widget.edit_contents()

    async def delete_message(self, msg_id: str) -> None:
        """ Method to delete an existing chat message """
        msg_widget = self._msg_map[msg_id]
        msg_widget.delete_contents()

    def inform_vote_has_started(self, started_by: str) -> None:
        """ Method that adds a widget to the screen informing that vote has started """
        msg = f"Vote has been started by {started_by}"
        widget = self.__create_announcement_widget(msg)
        self.__add_widget_to_screen(widget)

    def inform_vote_has_ended(self, conclusion: str) -> None:
        """ Method that adds a widget to the screen informing that vote has ended """
        widget = self.__create_announcement_widget(conclusion)
        self.__add_widget_to_screen(widget)

    def inform_game_has_ended(self, conclusion: str) -> None:
        """ Method that adds a widget to the screen informing that the game has ended """
        msg = f"-- The game has ended. {conclusion.capitalize()} --"
        widget = self.__create_announcement_widget(msg)
        self.__add_widget_to_screen(widget)

    def __create_announcement_widget(self, msg: str) -> Container:
        """ Helper method to create a widget for the voting status """
        widget = Static(msg, classes=self._css_class_announcement_widget)
        return Container(widget, classes=self._css_class_announcement_container)

    def __add_widget_to_screen(self, widget: ChatBubbleWidget | Widget | Container) -> None:
        """ Helper method to add the given widget to the screen """
        self.mount(widget)
        self.scroll_end(animate=False)

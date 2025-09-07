from dataclasses import dataclass
from typing import Callable, Optional, Type

from rich.console import Console, ConsoleOptions, RenderResult
from rich.padding import Padding
from rich.text import Text
from textual import on
from textual.reactive import reactive
from textual.widgets import OptionList
from textual.widgets.option_list import Option

from allms.config import RunTimeConfiguration
from allms.core.state import GameStateManager
from allms.core.chat import ChatMessage


@dataclass
class ModifyMessageOptionItemRenderable:
    """ Class for rendering each main-menu item in the list """
    timestamp: str
    title: str

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        timestamp = f"[dim]on {self.timestamp}[/]"
        msg_title = Text.from_markup(self.title)

        yield Padding(
            Text.assemble(msg_title, "\n", Text.from_markup(timestamp), overflow="ellipsis", no_wrap=True),
            pad=1
        )


class ModifyMessageOptionItem(Option):
    """ Class for each main-menu item in the list """

    def __init__(self, msg: ChatMessage, option_index: int):
        super().__init__(ModifyMessageOptionItemRenderable(msg.timestamp, msg.msg))
        self.msg = msg
        self.option_index = option_index

    def generate_renderable(self, edited: bool, deleted: bool = False) -> ModifyMessageOptionItemRenderable:
        """ Generates a new renderable based on whether the contents of the message has been changed """
        title_prefix = f"[i](edited)[/] "
        if deleted:
            title_prefix = f"[i](deleted)[/] "

        if (not edited) and (not deleted):
            title_prefix = ""

        new_title = title_prefix + self.msg.msg
        return ModifyMessageOptionItemRenderable(timestamp=self.msg.timestamp, title=new_title)


class ModifyMessageOptionListWidget(OptionList):
    """ Class for displaying list of messages sent """
    def __init__(self,
                 config: RunTimeConfiguration,
                 state_manager: GameStateManager,
                 edited_msgs_map: dict[str, str],
                 delete_msgs_set: set[str],
                 item_selected_callback: Type[Callable], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._config = config
        self._state_manager = state_manager
        self._edited_msgs_map = edited_msgs_map
        self._delete_msgs_set = delete_msgs_set
        self._item_selected_callback = item_selected_callback

        # Mapping between a message ID and the corresponding option
        self._msg_id_option_map: dict[str, ModifyMessageOptionItem] = {}
        self._curr_selected_msg: Optional[ChatMessage] = None

    def on_agent_changed(self, agent_id: str) -> None:
        """ Invoked when agent ID has been changed """
        self.clear_options()
        agent_msgs = self.__get_messages_by(agent_id)
        option_items = [ModifyMessageOptionItem(msg, i) for (i, msg) in enumerate(agent_msgs)]
        self._msg_id_option_map = {msg.id: option for (msg, option) in zip(agent_msgs, option_items)}

        self.add_options(option_items)

        # Update the display text if the message was previously edited/deleted
        for oi in option_items:
            if (oi.msg.id in self._delete_msgs_set) or oi.msg.deleted:
                self.replace_option_prompt_at_index(oi.option_index, oi.generate_renderable(edited=False, deleted=True))
            elif oi.msg.id in self._edited_msgs_map:
                self.replace_option_prompt_at_index(oi.option_index, oi.generate_renderable(edited=True))

        msg = None
        if len(option_items) > 0:
            self.highlighted = 0
            msg = agent_msgs[0]

        self._curr_selected_msg = msg
        self._item_selected_callback(msg)

    def on_message_content_changed(self, new_msg: str) -> None:
        """ Invoked when message content is changed in the textbox """
        msg = self._curr_selected_msg
        if msg is None:
            return

        # Update the display text of the option item if new contents are different from original
        assert msg.id in self._msg_id_option_map, f"Message ({msg}) is not present in the mapping"
        option_item = self._msg_id_option_map[self._curr_selected_msg.id]
        edited = (new_msg != msg.msg)
        delete = (msg.id in self._delete_msgs_set) or msg.deleted
        self.replace_option_prompt_at_index(option_item.option_index, option_item.generate_renderable(edited, delete))

    def __get_messages_by(self, agent_id: str) -> list[ChatMessage]:
        """
        Helper method to return the messages sent by the given agent
        """
        return self._state_manager.get_messages_sent_by(agent_id)

    @on(OptionList.OptionSelected)
    @on(OptionList.OptionHighlighted)
    async def handler_option_selected(self, event: OptionList.OptionSelected) -> None:
        """ Handler for handling events when an item is selected """
        self._curr_selected_msg = event.option.msg
        self._item_selected_callback(self._curr_selected_msg)

from typing import Any, Callable

from allms.utils.callbacks import BaseCallbackType, BaseCallbacks


class ChatCallbackType(BaseCallbackType):
    """ Class for storing the callback types for the chat """

    NEW_MESSAGE_RECEIVED: str = "new_message_received"
    ANNOUNCE_EVENT: str = "announce_event"
    UPDATE_AGENTS_LIST: str = "update_agents_list"
    IS_TYPING: str = "is_typing"
    TERMINATE_ALL_TASKS: str = "terminate_all_tasks"
    NOTIFY_TOAST: str = "notify_toast"
    CLOSE_CHATROOM: str = "close_chat"
    GAME_HAS_ENDED: str = "game_has_ended"


class ChatCallbacks(BaseCallbacks):
    """ Class containing the callbacks of the chat """

    def __init__(self, callback_mappings: dict[ChatCallbackType, Callable[..., Any]] = None):
        super().__init__(callback_mappings)

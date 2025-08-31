from typing import Any, Callable

from allms.utils.callbacks import BaseCallbackType, BaseCallbacks


class ChatCallbackType(BaseCallbackType):
    """ Class for storing the callback types for the chat """

    NEW_MESSAGE_RECEIVED: str = "new_message_received"
    VOTE_HAS_STARTED: str = "vote_has_started"
    VOTE_HAS_ENDED: str = "vote_has_ended"
    UPDATE_AGENTS_LIST: str = "update_agents_list"
    TERMINATE_ALL_TASKS: str = "terminate_all_tasks"


class ChatCallbacks(BaseCallbacks):
    """ Class containing the callbacks of the chat """

    def __init__(self, callback_mappings: dict[ChatCallbackType, Callable[..., Any]] = None):
        super().__init__(callback_mappings)

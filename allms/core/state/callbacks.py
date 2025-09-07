from typing import Any, Callable

from allms.utils.callbacks import BaseCallbackType, BaseCallbacks


class StateManagerCallbackType(BaseCallbackType):
    """ Class for storing the state manager callback types """

    GET_RECENT_MESSAGE_IDS: str = "get_recent_message_ids"
    GET_MESSAGE_WITH_ID: str = "get_message_with_id"
    IS_TYPING: str = "is_typing"
    SEND_MESSAGE: str = "send_message"
    VOTE_HAS_STARTED: str = "vote_started"
    START_A_VOTE: str = "start_vote"
    VOTE_FOR: str = "vote_for"
    END_THE_VOTE: str = "end_vote"
    UPDATE_UI_ON_NEW_MESSAGE: str = "update_ui"


class StateManagerCallbacks(BaseCallbacks):
    """ Class containing the callbacks of the state manager required by the chat-loop class """

    def __init__(self, callback_mappings: dict[StateManagerCallbackType, Callable[..., Any]] = None):
        super().__init__(callback_mappings)

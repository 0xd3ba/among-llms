from typing import Any, Callable

from allms.utils.callbacks import BaseCallbackType, BaseCallbacks


class StateManagerCallbackType(BaseCallbackType):
    """ Class for storing the state manager callback types """

    GET_RECENT_MESSAGE_IDS = "get_recent_message_ids"
    GET_MESSAGE_WITH_ID = "get_message_with_id"
    SEND_MESSAGE = "send_message"
    VOTE_HAS_STARTED = "vote_started"
    START_A_VOTE = "start_vote"
    VOTE_FOR = "vote_for"
    END_THE_VOTE = "end_vote"
    UPDATE_UI_ON_NEW_MESSAGE = "update_ui"


class StateManagerCallbacks(BaseCallbacks):
    """ Class containing the callbacks of the state manager required by the chat-loop class """

    def __init__(self, callback_mappings: dict[StateManagerCallbackType, Callable[..., Any]] = None):
        super().__init__(callback_mappings)

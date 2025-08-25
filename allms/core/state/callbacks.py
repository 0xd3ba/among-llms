import asyncio
import inspect
import logging
from enum import Enum
from typing import Any, Type, Callable

from allms.config import AppConfiguration


class CallbackType(str, Enum):
    """ Class for storing the callback types """

    GET_RECENT_MESSAGE_IDS = "get_recent_message_ids"
    GET_MESSAGE_WITH_ID = "get_message_with_id"
    SEND_MESSAGE = "send_message"
    START_A_VOTE = "start_vote"
    VOTE_FOR = "vote_for"
    END_THE_VOTE = "end_vote"
    UPDATE_UI_ON_NEW_MESSAGE = "update_ui"


class StateManagerCallbacks:
    """ Class containing the callbacks of the state manager required by the chat-loop class """

    def __init__(self, callback_mappings: dict[CallbackType, Callable[..., Any]] = None):
        if callback_mappings is None:
            callback_mappings = {}
        self._callback_mappings = callback_mappings

    def register_callback(self, callback_type: CallbackType, callback: Callable[..., Any]) -> None:
        """ Method to register a callback """
        if callback_type in self._callback_mappings:
            prev_callback = self._callback_mappings[callback_type]
            AppConfiguration.logger.log(f"Overwriting {callback_type} with new callback: {callback.__name__}. " +
                                        f"(previous callback: {prev_callback.__name__})",
                                        level=logging.WARNING)
        self._callback_mappings[callback_type] = callback

    async def invoke(self, callback_type: CallbackType, *args, **kwargs) -> Any:
        if callback_type not in self._callback_mappings:
            raise KeyError(f"{callback_type} not in registered callbacks: {list(self._callback_mappings.keys())}")

        callback = self._callback_mappings[callback_type]
        if inspect.iscoroutinefunction(callback):
            return await callback(*args, **kwargs)
        else:
            return callback(*args, **kwargs)

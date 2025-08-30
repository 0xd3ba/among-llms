import inspect
import logging
from enum import Enum
from typing import Any, Type, Callable

from allms.config import AppConfiguration


class BaseCallbackType(str, Enum):
    """ Base class for storing the callback types """
    pass


class BaseCallbacks:
    """ Base class containing the callbacks  """

    def __init__(self, callback_mappings: dict[BaseCallbackType, Callable[..., Any]] = None):
        if callback_mappings is None:
            callback_mappings = {}
        self._callback_mappings = callback_mappings

    def register_callback(self, callback_type: BaseCallbackType, callback: Callable[..., Any]) -> None:
        """ Method to register a callback """
        if callback_type in self._callback_mappings:
            prev_callback = self._callback_mappings[callback_type]
            AppConfiguration.logger.log(f"Overwriting {callback_type} with new callback: {callback.__name__}. " +
                                        f"(previous callback: {prev_callback.__name__})",
                                        level=logging.WARNING)
        self._callback_mappings[callback_type] = callback

    async def invoke(self, callback_type: BaseCallbackType, *args, **kwargs) -> Any:
        if callback_type not in self._callback_mappings:
            raise KeyError(f"{callback_type} not in registered callbacks: {list(self._callback_mappings.keys())}")

        callback = self._callback_mappings[callback_type]
        if inspect.iscoroutinefunction(callback):
            return await callback(*args, **kwargs)
        else:
            return callback(*args, **kwargs)

import logging
from typing import Any, Iterable

from allms.config import AppConfiguration


class SavingUtils:

    @staticmethod
    def properly_serialize_json(data: dict[Any, Any]) -> dict[Any: Any]:
        """ Properly serializes the given data dictionary into JSON serializable object """

        def _convert(obj: Any) -> Any:
            # Base types
            if isinstance(obj, (str, int, float, bool, bytes)) or (obj is None):
                return obj

            # Dictionary types: dict, Counter, OrderedDict etc.
            if isinstance(obj, dict):
                return {k: _convert(v) for (k, v) in obj.items()}

            # Iterable types (lists, sets, deque)
            if isinstance(obj, Iterable):
                return [_convert(item) for item in obj]

            # Technically this should not arrive to this branch. If it does, need to rethink about the datatype used
            AppConfiguration.logger.log(f"Unknown type ({type(obj)}) received for {obj}. Converting to string ...",
                                        level=logging.WARNING)
            return str(obj)

        # Recursively format the data
        # Needed because some data structures like sets are not JSON serializable
        fmt_data = _convert(data)
        return fmt_data

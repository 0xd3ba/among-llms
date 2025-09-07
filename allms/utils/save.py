from __future__ import annotations
import logging
from collections import OrderedDict, deque
from collections.abc import Iterable, Mapping
from dataclasses import fields, Field, is_dataclass
from typing import Any, get_origin, get_args, get_type_hints, Iterable, Type, TypeVar, Union

from allms.config import AppConfiguration


class SavingUtils:

    T = TypeVar("T")  # Generic type

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

    @staticmethod
    def properly_deserialize_json(cls: Type[SavingUtils.T], data: dict[Any, Any]) -> SavingUtils.T:
        """ Properly deserializes the given data dictionary to a dataclass """
        if not is_dataclass(cls):
            raise ValueError(f"{cls} is not a valid dataclass")

        hints = get_type_hints(cls)
        init_kwargs = {}
        iterable_types = [list, set, tuple, deque]

        for f in fields(cls):
            field_value = data.get(f.name)
            # Note: f.type will be a string because it is a forward reference, need to resolve it using hints[...]
            field_type = hints[f.name]

            if field_value is None:
                init_kwargs[f.name] = None
                continue

            # Optional[X] types
            # IMPORTANT: This only supports two types, i.e. Optional[Class] (equivalent to: Class | None)
            # This won't work for cases like Optional[Class_1 | Class_2 | ... | Class_N] which has N+1 types
            # In our case, since it code has only two types, this works (for now)
            origin = get_origin(field_type)
            args = get_args(field_type)
            if (origin is Union) and type(None) in args:
                # Extract the inner type depending on how Class | None is represented:
                #   - Union[Class, None]
                #   - Union[None, Class]
                inner_type = args[0] if (args[0] is not type(None)) else args[1]
                field_type = inner_type
                origin = get_origin(field_type)
                args = get_args(field_type)

            # Nested dataclass types
            if is_dataclass(field_type) and isinstance(field_value, dict):
                init_kwargs[f.name] = SavingUtils.properly_deserialize_json(cls=field_type, data=field_value)

            # Iterable types (in our case, we have lists, tuples, sets, deques)
            elif (origin in iterable_types) or isinstance(field_value, tuple(iterable_types)):
                item_type = args[0] if args else Any
                converted_items = []
                for item in field_value:
                    if is_dataclass(item_type) and isinstance(item, dict):
                        converted_items.append(SavingUtils.properly_deserialize_json(cls=item_type, data=item))
                    else:
                        converted_items.append(item)

                target_type = origin or type(field_value)
                if target_type == deque:
                    converted_items = SavingUtils.__reconstruct_deque(field=f, items=converted_items)
                else:
                    converted_items = target_type(converted_items)

                init_kwargs[f.name] = converted_items

            # Mapping types:
            # # Dict[K, V] or OrderedDict[K, V] or any Mapping
            elif isinstance(field_value, Mapping):
                target_type = get_origin(field_type) or field_type
                key_type, val_type = (Any, Any)

                args = get_args(field_type)
                if args:
                    key_type, val_type = args

                converted_dict = {}
                for k, v in field_value.items():
                    if is_dataclass(val_type) and isinstance(v, dict):
                        converted_dict[k] = SavingUtils.properly_deserialize_json(cls=val_type, data=v)
                    else:
                        converted_dict[k] = v
                init_kwargs[f.name] = target_type(converted_dict)

            # Basic types or we missed some case ?
            # If it is the latter, then need to look into it
            else:
                if type(field_value) not in (int, float, bool, str, bytes):
                    AppConfiguration.logger.log(f"Falling back to direct assignment due to unknown type for {f.name}: {field_value}")
                init_kwargs[f.name] = field_value

        return cls(**init_kwargs)

    @staticmethod
    def __reconstruct_deque(field: Field, items: Iterable[Any]) -> deque:
        """ Helper method to reconstruct the deque as per the data-class's default factory """
        n = None
        try:
            if (field.default_factory is not None) and callable(field.default_factory):
                tmp_dq = field.default_factory()
                if isinstance(tmp_dq, deque):
                    n = tmp_dq.maxlen
        except Exception:
            pass
        return deque(items, maxlen=n)

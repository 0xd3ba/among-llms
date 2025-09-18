from dataclasses import dataclass, field

from .types import ModelTypes


@dataclass
class BaseModelConfiguration:
    """ Base class for all models """
    model_type: ModelTypes
    offline: bool
    online: bool
    reasoning_levels: frozenset[str] = field(default_factory=frozenset)
    _model_name: str = ""

    def __post_init__(self):
        self._model_name = self.model_type.value
        self.reasoning_levels = frozenset([rl.lower() for rl in self.reasoning_levels])

    def reasoning_level_is_supported(self, level: str) -> bool:
        """ Returns True if the given reasoning level is supported """
        return level.lower() in self.reasoning_levels

    def __hash__(self) -> int:
        """Hash based on model name """
        return hash((self._model_name, self.offline, self.online))

    def __eq__(self, other: object) -> bool:
        """Equality is based on model name"""
        if not isinstance(other, BaseModelConfiguration):
            return NotImplemented

        return (self._model_name, self.offline, self.online) == (other._model_name, other.offline, other.online)


class OpenAIGPTModel(BaseModelConfiguration):
    """ Class for OpenAI GPT models """
    def __init__(self, model_type: ModelTypes, offline: bool, online: bool):
        reasoning_levels = ["low", "medium", "high"]
        super().__init__(model_type=model_type, offline=offline, online=online, reasoning_levels=reasoning_levels)

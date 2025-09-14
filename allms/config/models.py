import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ModelTypes(str, Enum):
    """ Class containing the supported models """
    gpt_oss_20b: str = "gpt-oss:20b"
    gpt_oss_120b: str = "gpt-oss:120b"

    # Add the names of your models here


@dataclass
class BaseModelConfiguration:
    """ Base class for all models """
    model_type: ModelTypes
    offline_model: bool
    env_var_api_key: str
    model_name: str = ""
    reasoning_levels: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self):
        self.model_name = self.model_type.value
        self.reasoning_levels = frozenset(self.reasoning_levels)

        # Check if online model and we have provided a valid environment variable
        if not self.offline_model:
            self.__check_validity_of_env_var()

    def __check_validity_of_env_var(self) -> None:
        """ Helper method to check if the provided environment variable is valid for an online model """
        # Check 1: Did the user provide a variable name?
        if not self.env_var_api_key:
            raise ValueError(
                f"{self.model_name} is an online model but no environment variable name was provided."
            )

        # Check 2: Does the variable exist and is it non-empty ?
        if not os.getenv(self.env_var_api_key):
            raise ValueError(
                f"{self.model_name} is an online model, but the environment variable "
                f"[{self.env_var_api_key}] is not set or is empty."
            )

    def __hash__(self) -> int:
        """Hash based on (name, offline_model) """
        return hash((self.model_name, self.offline_model))

    def __eq__(self, other: object) -> bool:
        """Equality is based on (name, offline_model)."""
        if not isinstance(other, BaseModelConfiguration):
            return NotImplemented
        return (self.model_name, self.offline_model) == (other.model_name, other.offline_model)


class OpenAIGPTModel(BaseModelConfiguration):
    """ Class for OpenAI GPT models """
    def __init__(self, model_type: ModelTypes, offline_model: bool, env_var_api_key: Optional[str] = None):
        reasoning_levels = ["low", "medium", "high"]
        super().__init__(model_type=model_type, offline_model=offline_model, reasoning_levels=reasoning_levels, env_var_api_key=env_var_api_key)

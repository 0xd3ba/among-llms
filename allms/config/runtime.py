from __future__ import annotations
import os
from dataclasses import field
from pathlib import Path

from pydantic import field_validator, model_validator
from pydantic.dataclasses import dataclass

from .app import AppConfiguration
from .models import ModelTypes
from .ollama import OllamaConfiguration


@dataclass(frozen=True)
class RunTimeModel:
    name: str
    offline_model: bool
    reasoning_level: str
    env_var_api_key: str
    offline_server_port: int = OllamaConfiguration.default_local_port

    @field_validator("offline_server_port")
    def _validate_port(cls, v: int) -> int:
        if v < 0:
            raise ValueError(f"The Ollama server port must be a positive integer but got {v} instead")
        return v

    @model_validator(mode="after")
    def _validate(cls, model: RunTimeModel) -> RunTimeModel:
        # Validate the supplied model configuration
        # 1. Check if the model is supported
        ai_models_map = AppConfiguration.ai_models
        ai_model_type = ModelTypes(model.name)  # Will throw ValueError if not present

        if ai_model_type not in ai_models_map:
            raise ValueError(f"{model.name} is not present inside AppConfiguration's supported models. Did you forget to add an entry?")
        ai_model = AppConfiguration.ai_models[ai_model_type]

        # 2: Check if the model requested to be used offline and it is supported
        if model.offline_model:
            if not ai_model.offline:
                raise ValueError(
                    f"{model.name} is requested to be used as an OFFLINE model but the mapping inside AppConfiguration "
                    f"only supports offline={ai_model.offline}, online={ai_model.online}. Did you forget updating it?"
                )

        # Online model
        else:
            # 3. Check if it is supported
            if not ai_model.online:
                raise ValueError(
                    f"{model.name} is requested to be used as an ONLINE model but the mapping inside AppConfiguration "
                    f"only supports offline={ai_model.offline}, online={ai_model.online}. Did you forget updating it?"
                )

            # 4. Check if environment variable was provided
            if not model.env_var_api_key:
                raise ValueError(f"{model.name} is an online model but no environment variable name was provided.")

            # 5. Is the environment variable non-empty ?
            if not os.getenv(model.env_var_api_key):
                raise ValueError(
                    f"{model.name} is an online model, but the environment variable "
                    f"[{model.env_var_api_key}] is not set or is empty."
                )

        # 6. Check if the provided reasoning level is supported
        if not ai_model.reasoning_level_is_supported(model.reasoning_level):
            raise ValueError(
                f"Provided reasoning_level={model.reasoning_level} is not supported. "
                f"Supported levels: {sorted(list(ai_model.reasoning_levels))}"
            )

        return model


@dataclass(frozen=True)
class RunTimeConfiguration:
    """ Configuration class holding constants from CLI and YAML config file """
    maximum_agent_count: int
    default_agent_count: int
    response_delay_min_seconds: int
    response_delay_max_seconds: int
    enable_rag: bool
    show_thought_process: bool
    show_suspects: bool
    save_directory: str
    skip_intro: bool
    ui_developer_mode: bool
    use_models: list[RunTimeModel] = field(default_factory=list)

    def __post_init__(self):
        self.__mkdir(self.save_directory)

    @field_validator("maximum_agent_count", "default_agent_count")
    def _validate_agent_count(cls, v: int) -> int:
        if v < AppConfiguration.min_agent_count:
            raise ValueError(f"Agent count should be >= {AppConfiguration.min_agent_count} but got {v} instead")
        return v

    @field_validator("response_delay_min_seconds", "response_delay_max_seconds")
    def _validate_response_delays(cls, v: int) -> int:
        if v < 0:
            raise ValueError(f"Response delay should be a positive number but got {v} instead")
        return v

    @field_validator("save_directory")
    def _validate_directory(cls, v: str) -> str:
        path = Path(v)
        if not path.is_dir():
            raise ValueError(f"Expecting path={path} to be a directory")
        return v

    @staticmethod
    def __mkdir(path: str) -> None:
        """ Helper method to create the given directory if it doesn't exist """
        path = Path(path)
        try:
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise RuntimeError(f"There was an issue creating the given directory: {str(path)}")

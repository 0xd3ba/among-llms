from __future__ import annotations
from dataclasses import field
from pathlib import Path

from pydantic import field_validator, model_validator
from pydantic.dataclasses import dataclass

from .app import AppConfiguration


@dataclass(frozen=True)
class RunTimeModel:
    name: str
    offline_model: bool
    reasoning_level: str
    env_var_api_key: str
    offline_server_port: int = 11434  # Default port used by local Ollama server

    @field_validator("offline_server_port")
    def _validate_port(cls, v: int) -> int:
        if v < 0:
            raise ValueError(f"The Ollama server port must be a positive integer but got {v} instead")
        return v

    @model_validator(mode="after")
    def _validate_model_name(cls, model: RunTimeModel) -> RunTimeModel:
        # Check if the model is supported
        supported_models = {(model.model_name, model.offline_model) for model in AppConfiguration.ai_models}
        if (model.name, model.offline_model) not in supported_models:
            raise ValueError(f"({model.name}, {model.offline_model}) is not supported. Supported models: {supported_models}")

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

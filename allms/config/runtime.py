from dataclasses import field
from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class RunTimeConfiguration:
    """ Configuration class holding constants from CLI and YAML config file """

    ai_model: str
    offline_model: bool
    ai_reasoning_lvl: str
    max_agent_count: int
    default_agent_count: int
    enable_rag: bool
    show_thought_process: bool
    show_suspects: bool
    save_directory: str
    ui_dev_mode: bool
    skip_intro: bool

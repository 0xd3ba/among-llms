from dataclasses import dataclass
from pathlib import Path

import tzlocal

import allms.version as version
from .utils.time import Time
from .utils.logger import AppLogger


class AppConfiguration:
    """ Class for any configuration required for setting up the app """

    # Description of the app
    app_name: str = "Among LLMs"
    app_tagline: list[str] = ["One human. Multiple bots.", "Do whatever it takes to not get caught!"]
    app_version: str = version.__version__
    app_repo: str = "https://github.com/0xd3ba/among-llms"
    app_dev: str = "0xd3ba"
    app_hackathon: str = "OpenAI Open Model Hackathon 2025"

    # Timezone of the clock
    timezone: str = tzlocal.get_localzone_name()
    clock: Time = Time(timezone)

    # Logging configuration
    log_dir = "./logs"
    logger = AppLogger(clock=clock, log_dir=log_dir)

    # List of AI models supported
    ai_models: list[str] = [
        "gpt-oss-20b",
        "gpt-oss-120b",
    ]

    ai_reasoning_levels: list[str] = [
        "low",
        "medium",
        "high"
    ]

    # Max. number of retries allowed by an agent for an invalid response
    max_model_retries: int = 3

    # Minimum number of agents that should be in the game
    min_agent_count: int = 3

    # Context size for the model -- Max. no. of messages in the chat history (public messages, DMs and notifications)
    # the model gets as context for generating a reply
    # Note(s):
    #   - Changing this to a larger value may reduce the performance as the models may take longer to produce replies
    max_lookback_messages: int = 25

    # Path of the resource files
    __resource_dir_root = Path(__file__).parent / "res"
    resource_persona_path = __resource_dir_root / "persona.yml"
    resource_scenario_path = __resource_dir_root / "scenario.yml"


class StyleConfiguration:
    """ Class holding constants for styling purposes """
    class_border: str = "border"
    class_border_highlight: str = "highlight-border"
    class_modal_container: str = "modal-container"


class BindingConfiguration:
    """ Class holding the global hotkey bindings """
    # Bindings for modal screens
    modal_close_screen: str = "ctrl+w"

    # Bindings for new chat creation screen
    new_chat_randomize_scenario: str = "ctrl+r"
    new_chat_randomize_agent_persona: str = "ctrl+r"
    new_chat_customize_agents: str = "ctrl+s"

    # Bindings for chat screen
    chatroom_show_scenario: str = "f1"
    chatroom_show_your_persona: str = "f2"
    chatroom_show_all_persona: str = "f3"
    chatroom_modify_msgs: str = "f4"
    chatroom_send_message: str = "enter"

    # Bindings for modify message screen
    modify_msgs_mark_unmark_delete: str = "ctrl+x"


@dataclass
class RunTimeConfiguration:
    """ Configuration class holding constants from CLI and YAML config file """

    ai_model: str
    offline_model: bool
    ai_reasoning_lvl: str
    max_agent_count: int
    default_agent_count: int
    enable_rag: bool
    ui_dev_mode: bool
    skip_intro: bool

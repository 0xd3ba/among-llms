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

    # List of AI models supported
    ai_models: list[str] = [
        "gpt-oss:20b",
        "gpt-oss:120b",
    ]

    ai_reasoning_levels: list[str] = [
        "low",
        "medium",
        "high"
    ]

    default_genre: str = "sci-fi"  # The default scenario/persona genre. Must exist within scenario directory

    # Max. number of retries allowed by an agent for an invalid response
    max_model_retries: int = 3

    # Minimum number of agents that should be in the game
    min_agent_count: int = 3

    # Context size for the model -- Max. no. of messages in the chat history (public messages, DMs and notifications)
    # the model gets as context for generating a reply
    # Note(s):
    #   - Changing this to a larger value may reduce the performance as the models may take longer to produce replies
    max_lookback_messages: int = 25

    # Maximum duration of an active vote (in minutes)
    max_vote_duration_min: int = 10

    # Path of the resource directories and other files
    __parent_dir: Path = Path(__file__).parent
    __resource_dir_root: Path = __parent_dir / "res"
    __data_dir_root: Path = __parent_dir.parent / "data"

    # Resource configuration
    resource_scenario_dir = __resource_dir_root / "scenarios"
    resource_names_dir = __resource_dir_root / "names"
    resource_persona_yml = "persona.yml"
    resource_scenario_yml = "scenario.yml"
    resource_name_yml = "names.yml"

    # Logging configuration
    log_dir = __data_dir_root / "logs"
    logger = AppLogger(clock=clock, log_dir=log_dir)


class StyleConfiguration:
    """ Class holding constants for styling purposes """
    class_border: str = "border"
    class_border_highlight: str = "highlight-border"
    class_modal_container: str = "modal-container"


class ToastConfiguration:
    """ Class holding constants for toasts """
    type_information: str = "information"
    type_warning: str = "warning"
    type_error: str = "error"

    timeout: float = 2.0  # How long (in seconds) a toast is displayed on the screen


class BindingConfiguration:
    """ Class holding the global hotkey bindings """
    # Bindings for modal screens
    modal_close_screen: str = "ctrl+w"

    # Bindings for new chat creation screen
    new_chat_randomize_scenario: str = "ctrl+r"
    new_chat_randomize_agent_persona: str = "ctrl+r"
    new_chat_customize_agents: str = "ctrl+s"
    new_chat_load_from_saved: str = "ctrl+l"

    # Bindings for chat screen
    chatroom_show_scenario: str = "f1"
    chatroom_show_your_persona: str = "f2"
    chatroom_show_all_persona: str = "f3"
    chatroom_modify_msgs: str = "f4"
    chatroom_start_vote: str = "f5"
    chatroom_send_message: str = "enter"
    chatroom_quit: str = "ctrl+w"

    # Bindings for modify message screen
    modify_msgs_mark_unmark_delete: str = "ctrl+x"


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

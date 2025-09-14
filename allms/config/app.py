from pathlib import Path

import tzlocal

import allms.version as version
from allms.utils.time import Time
from allms.utils.logger import AppLogger


class AppConfiguration:
    """ Class for any configuration required for setting up the app """

    # Description of the app
    app_name: str = "Among LLMs"
    app_tagline: list[str] = ["One human. Multiple bots.", "Do whatever it takes to not get caught!"]
    app_version: str = version.__version__
    app_repo: str = "https://github.com/0xd3ba/among-llms"
    app_dev: str = "0xd3ba"
    app_dev_email: str = "0xd3ba@gmail.com"
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
    max_lookback_messages: int = 30

    # Maximum duration of an active vote (in minutes)
    max_vote_duration_min: int = 10

    # Path of the resource directories and other files
    __parent_dir: Path = Path(__file__).parent.parent
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

from pathlib import Path

import tzlocal

import allms.version as version
from allms.config.models import *
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

    # AI models supported
    ai_models: dict[ModelTypes, BaseModelConfiguration] = {
        ModelTypes.gpt_oss_20b: OpenAIGPTModel(model_type=ModelTypes.gpt_oss_20b, offline=True, online=False),
        ModelTypes.gpt_oss_120b: OpenAIGPTModel(model_type=ModelTypes.gpt_oss_120b, offline=True, online=False),
    }

    default_genre: str = "sci-fi"  # The default scenario/persona genre. Must exist within scenario directory

    # Max. number of retries allowed by an agent for an invalid response
    max_model_retries: int = 3

    # Minimum number of agents that should be in the game
    min_agent_count: int = 3

    # Min. context size for the model -- Max. no. of messages in the chat history (public messages, DMs and notifications)
    min_lookback_messages: int = 10

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

from dataclasses import dataclass

import tzlocal

import allms.version as version
from .utils.time import Time


class AppConfiguration:
    """ Class for any configuration required for setting up the app """

    # Description of the app
    app_name: str = "Among LLMs"
    app_tagline: str = "The only one sus here is you. Type wisely as the LLMs are watching ..."
    app_version: str = version.__version__
    app_repo: str = "https://github.com/0xd3ba/among-llms"
    app_dev: str = "0xd3ba"

    # Timezone of the clock
    timezone: str = tzlocal.get_localzone_name()
    clock: Time = Time(timezone)

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

    # Minimum number of agents that should be in the game
    min_agent_count: int = 3


@dataclass
class RunTimeConfiguration:
    """ Configuration class holding constants from CLI and YAML config file """

    ai_model: str
    ai_reasoning_lvl: str
    max_agent_count: int
    skip_intro: bool

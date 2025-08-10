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
    # Must be a valid timezone from pytz.all_timezones
    timezone: str = "US/Eastern"
    clock: Time = Time(timezone)

    # List of AI models
    # Format: (model_name, is_local_model)
    ai_models: list[str] = [
        ("gpt-oss-20b", True),
        ("gpt-oss-120b", True),
        # Add other models if needed
    ]

    ai_reasoning_levels: list[str] = [
        "low",
        "medium",
        "deep"
    ]

    # Max. number of agents to use per chatroom
    # Note: Setting it to a large number may cause severe performance issues (unless using an AI model from cloud)
    max_agents: int = 10
    default_n_agents: int = 5


class StyleConfiguration:
    """ Class for any configuration required for styling the app """

    # CSS style related classes
    css_class_round_border: str = "round_border"
    css_class_highlight_border_on_focus: str = "highlight_border"

import allms.version as version
from .utils.time import Time


class AppConfiguration:

    # Description of the app
    app_name: str = "Among LLMs"
    app_tagline: str = "The only one sus here is you. Type wisely as the LLMs are watching ..."
    app_version: str = version.__version__
    app_repo: str = "https://github.com/0xd3ba/among-llms"

    # Timezone of the clock
    # Must be a valid timezone from pytz.all_timezones
    timezone: str = "US/Eastern"
    clock: Time = Time(timezone)


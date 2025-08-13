import sys
import logging
from argparse import ArgumentParser

from allms.config import AppConfiguration
from allms.utils.parser import YAMLConfigFileParser
from .cli import AmongLLMs


def parse_args(args: list[str]) -> tuple:
    """ Helper method to build a parser and parse the arguments """
    parser = ArgumentParser()
    parser.add_argument("-c", "--config", type=str, default="config.yml", help="/path/to/config/file")

    args_list = parser.parse_args(args)

    # Reserved some space for future additions (if any)
    return args_list.config, None


def main():
    config_path, _ = parse_args(sys.argv[1:])

    # Validate the configuration before starting the app
    config_parser = YAMLConfigFileParser(config_path)
    config_parser.parse()

    ai_model = config_parser.ai_model
    ai_reasoning_lvl = config_parser.reasoning_level
    max_agent_count = config_parser.max_agent_count
    is_error = False

    if ai_model not in AppConfiguration.ai_models:
        logging.error(f"Given model({ai_model}) is not supported. Supported models: {AppConfiguration.ai_models}")
        is_error = True

    if ai_reasoning_lvl not in AppConfiguration.ai_reasoning_levels:
        logging.error(f"Given reasoning-level({ai_reasoning_lvl}) is not supported. Supported levels: {AppConfiguration.ai_reasoning_levels}")
        is_error = True

    try:
        max_agent_count_int = int(max_agent_count)
        if max_agent_count_int <= AppConfiguration.min_agent_count:
            raise RuntimeError
    except ValueError:
        logging.error(f"Max. number of agents must be an integer but got {max_agent_count} instead")
        is_error = True
    except RuntimeError:
        logging.error(f"Max. number of agents must be atleast >= {AppConfiguration.min_agent_count} but got {max_agent_count_int} instead")
        is_error = True

    if is_error:
        logging.critical(f"Unable to start the application due to invalid configuration. Exiting the app ... ")
        sys.exit(-1)

    # No error -- Fire up the application
    app = AmongLLMs(ai_model=ai_model, ai_reasoning_lvl=ai_reasoning_lvl, max_agent_count=max_agent_count_int)
    app.run()


if __name__ == '__main__':
    main()

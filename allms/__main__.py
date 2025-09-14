import logging
import sys
from argparse import ArgumentParser
from typing import Optional

from allms.config import AppConfiguration, RunTimeConfiguration
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
    config_path, *_ = parse_args(sys.argv[1:])
    runtime_config: Optional[RunTimeConfiguration] = None

    try:
        yml_parser = YAMLConfigFileParser(config_path)
        runtime_config = yml_parser.parse()
    except (ValueError, RuntimeError, Exception) as e:
        logging.critical(f"Unable to start the application due to invalid configuration: {e}")
        logging.critical(f"Exiting the app ...")
        sys.exit(-1)

    # No error -- Ready to fire up the app
    # Preload the sentence transformer before starting the app to avoid performance issues in the UI
    if runtime_config.enable_rag:
        AppConfiguration.logger.log(f"RAG is currently not supported. Ignoring the setting.", level=logging.WARNING)
        # TODO: Pre-load the sentence transformer

    # Remove the handler that outputs the logs to the console as it may cause visual glitches in the UI
    AppConfiguration.logger.remove_handler_of_console_stream()

    app = AmongLLMs(runtime_config)
    app.run()

    AppConfiguration.logger.add_handler_of_console_stream()


if __name__ == '__main__':
    main()

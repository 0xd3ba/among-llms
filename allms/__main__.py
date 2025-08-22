import asyncio
import logging
import sys
from argparse import ArgumentParser

from allms.config import AppConfiguration, RunTimeConfiguration
from allms.core.chat.database import SingletonSentenceTransformer
from allms.utils.parser import YAMLConfigFileParser
from .cli import AmongLLMs


def parse_args(args: list[str]) -> tuple:
    """ Helper method to build a parser and parse the arguments """
    parser = ArgumentParser()
    parser.add_argument("-c", "--config", type=str, default="config.yml", help="/path/to/config/file")
    parser.add_argument("-s", "--skip-intro", type=bool, default=False, help="Skip intro splash screen?")

    args_list = parser.parse_args(args)

    # Reserved some space for future additions (if any)
    return args_list.config, args_list.skip_intro, None


def main():
    config_path, skip_intro, *_ = parse_args(sys.argv[1:])

    try:
        yml_parser = YAMLConfigFileParser(config_path)
        yml_parser.parse()
        yml_parser.validate()
    except RuntimeError:
        logging.critical(f"Unable to start the application due to invalid configuration. Exiting the app ... ")
        sys.exit(-1)

    # No error -- Bundle the configuration and fire up the app
    min_agent_count = AppConfiguration.min_agent_count
    default_agent_count = (min_agent_count + yml_parser.max_agent_count) // 2
    runtime_config = RunTimeConfiguration(ai_model=yml_parser.ai_model,
                                          ai_reasoning_lvl=yml_parser.reasoning_level,
                                          max_agent_count=yml_parser.max_agent_count,
                                          enable_rag=yml_parser.enable_rag,
                                          ui_dev_mode=yml_parser.ui_dev_mode,
                                          default_agent_count=default_agent_count,
                                          skip_intro=skip_intro)

    # Preload the sentence transformer before starting the app to avoid performance issues in the UI
    if yml_parser.enable_rag:
        AppConfiguration.logger.info(f"Please wait while sentence-transformer is being loaded ...")
        _ = SingletonSentenceTransformer.get()

    app = AmongLLMs(runtime_config)
    app.run()


if __name__ == '__main__':
    main()

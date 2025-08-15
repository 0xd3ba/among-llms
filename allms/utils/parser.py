import logging
import pathlib

import yaml

from allms.config import AppConfiguration


class BaseYAMLParser:
    """ Base class for parsing YAML files """
    def __init__(self, file_path: str | pathlib.Path):
        self._file_path = pathlib.Path(file_path)
        assert self._file_path.exists(), f"Provided file: {file_path} doesn't exist. Make sure the path is correct"

        self._logger = logging.getLogger(self.__class__.__name__)

    def parse(self) -> dict:
        with open(self._file_path, "r") as f:
            yml_data = yaml.safe_load(f)

        expected_keys = [getattr(self.__class__, attr) for attr in dir(self.__class__) if attr.startswith("key_")]
        for ek in expected_keys:
            assert ek in yml_data, f"Expecting {ek} to be present in the YAML file but is missing. Did you miss it?"
        return yml_data
    
    def validate(self) -> None:
        """ Validates the parsed arguments. Needs to raise RuntimeError if validation fails """
        raise NotImplementedError


class YAMLConfigFileParser(BaseYAMLParser):
    """ Parser for the user configuration file """

    key_ai_model: str = "model"
    key_reasoning_level: str = "reasoningLevel"
    key_max_agent_count: str = "maximumAgentCount"

    def __init__(self, file_path: str | pathlib.Path):
        super().__init__(file_path)
        self.ai_model: str | None = None
        self.reasoning_level: str | None = None
        self.max_agent_count: int | None = None

    def parse(self) -> None:
        yml_data = super().parse()
        self.ai_model = yml_data[self.key_ai_model].lower()
        self.reasoning_level = yml_data[self.key_reasoning_level].lower()
        self.max_agent_count = yml_data[self.key_max_agent_count]

    def validate(self) -> None:
        """ Validates the parsed arguments """
        is_error = False
        if self.ai_model not in AppConfiguration.ai_models:
            is_error = True
            logging.error(f"Given model({self.ai_model}) is not supported. Supported models: {AppConfiguration.ai_models}")

        if self.reasoning_level not in AppConfiguration.ai_reasoning_levels:
            is_error = True
            logging.error(f"Given reasoning-level({self.reasoning_level}) is not supported." +
                          "Supported levels: {AppConfiguration.ai_reasoning_levels}")

        try:
            max_agent_count = int(self.max_agent_count)
            if max_agent_count <= AppConfiguration.min_agent_count:
                raise RuntimeError
            self.max_agent_count = int(self.max_agent_count)
        except ValueError:
            is_error = True
            logging.error(f"Max. number of agents must be an integer but got {self.max_agent_count} instead")
        except RuntimeError:
            is_error = True
            logging.error(f"Max. number of agents must be atleast >= {AppConfiguration.min_agent_count}" +
                          " but got {max_agent_count_int} instead")

        if is_error:
            raise RuntimeError(f"Invalid configuration received")

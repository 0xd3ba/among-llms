import logging
from pathlib import Path
from typing import Any

import yaml

from allms.config import AppConfiguration, RunTimeConfiguration


class BaseYAMLParser:
    """ Base class for parsing YAML files """
    def __init__(self, file_path: str | Path):
        self._file_path = Path(file_path)
        assert self._file_path.exists(), f"Provided file: {file_path} doesn't exist. Make sure the path is correct"

        self._logger = logging.getLogger(self.__class__.__name__)

    def parse(self, root_key: str = None) -> dict | list | Any:
        with open(self._file_path, "r", encoding="utf-8") as f:
            yml_data = yaml.safe_load(f)
            if root_key is not None:
                assert root_key in yml_data, f"Provided root key({root_key}) is not valid"
                yml_data = yml_data[root_key]

        expected_keys = self.get_yml_keys()
        for ek in expected_keys:
            assert ek in yml_data, f"Expecting {ek} to be present in the YAML file but is missing. Did you miss it?"
        return yml_data
    
    def validate(self, yml_data: dict = None) -> None:
        """ Validates the parsed arguments. Needs to raise RuntimeError/AssertionError if validation fails """
        raise NotImplementedError

    def get_yml_keys(self) -> list[str]:
        """ Method to get all the keys in the yml file """
        keys = [getattr(self.__class__, attr) for attr in dir(self.__class__) if attr.startswith("key_")
                and attr in self.__class__.__dict__]
        return keys


class YAMLConfigFileParser(BaseYAMLParser):
    """ Parser for the user configuration file """

    key_use_models: str = "use_models"
    key_max_agent_count: str = "maximum_agent_count"
    key_def_agent_count: str = "default_agent_count"
    key_response_delay_min: str = "response_delay_min_seconds"
    key_response_delay_max: str = "response_delay_max_seconds"
    key_max_lookback_msgs: str = "max_lookback_messages"
    key_enable_memory_compression: str = "enable_memory_compression"
    key_enable_rag: str = "enable_rag"
    key_show_thought_process: str = "show_thought_process"
    key_show_suspects: str = "show_suspects"
    key_save_directory: str = "save_directory"
    key_ui_dev_mode: str = "ui_developer_mode"
    key_skip_intro: str = "skip_intro"

    def __init__(self, file_path: str | Path):
        super().__init__(file_path)

    def parse(self, root_key: str = None) -> RunTimeConfiguration:
        yml_data: dict = super().parse()
        return RunTimeConfiguration(**yml_data)

    def validate(self, yml_data: dict = None) -> None:
        """ Validates the parsed arguments """
        return


class YAMLPersonaParser(BaseYAMLParser):
    """ Parser for the agent persona file """

    root: str = "personas"
    key_backgrounds: str = "backgrounds"
    key_characteristics: str = "characteristics"
    key_voices: str = "voices"

    def __init__(self, file_path: str | Path):
        super().__init__(file_path)

    def parse(self, root_key: str = None) -> dict:
        yml_data = super().parse(root_key=self.root)
        return yml_data

    def validate(self, yml_data: dict = None) -> None:
        assert yml_data is not None, f"Expected to receive the yml data for validation but received None instead"
        keys = self.get_yml_keys()

        # As long as each list has > 0 entries, we're good
        for key in keys:
            if not yml_data[key]:
                raise RuntimeError(f"Expected key={key} list to have > 0 entries but the list is empty")


class YAMLScenarioParser(YAMLPersonaParser):
    """ Parser for the scenario file """

    root: str = "scenarios"

    def __init__(self, file_path: str | Path):
        super().__init__(file_path)
        # Since it shares same functionality with Persona parser, just inherit it


class YAMLNamesParser(YAMLScenarioParser):
    """ Parser for the names file """

    root: str = "names"

    def __init__(self, file_path: str | Path):
        super().__init__(file_path)
        # Since it shares same functionality with Scenario parser, just inherit it

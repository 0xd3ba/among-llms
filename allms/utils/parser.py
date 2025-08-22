import logging
from pathlib import Path

import yaml

from allms.config import AppConfiguration


class BaseYAMLParser:
    """ Base class for parsing YAML files """
    def __init__(self, file_path: str | Path):
        self._file_path = Path(file_path)
        assert self._file_path.exists(), f"Provided file: {file_path} doesn't exist. Make sure the path is correct"

        self._logger = logging.getLogger(self.__class__.__name__)

    def parse(self, root_key: str = None) -> dict:
        with open(self._file_path, "r") as f:
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

    key_ai_model: str = "model"
    key_reasoning_level: str = "reasoningLevel"
    key_max_agent_count: str = "maximumAgentCount"
    key_enable_rag: str = "enableRAG"
    key_ui_dev_mode: str = "uiDeveloperMode"

    def __init__(self, file_path: str | Path):
        super().__init__(file_path)
        self.ai_model: str | None = None
        self.reasoning_level: str | None = None
        self.max_agent_count: int | None = None
        self.enable_rag: bool | None = None
        self.ui_dev_mode: bool | None = None

    def parse(self, root_key: str = None) -> dict:
        yml_data = super().parse()
        self.ai_model = yml_data[self.key_ai_model].lower()
        self.reasoning_level = yml_data[self.key_reasoning_level].lower()
        self.max_agent_count = yml_data[self.key_max_agent_count]
        self.enable_rag = yml_data[self.key_enable_rag]
        self.ui_dev_mode = yml_data[self.key_ui_dev_mode]
        return yml_data

    def validate(self, yml_data: dict = None) -> None:
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

        if not isinstance(self.enable_rag, bool):
            is_error = True
            logging.error(f"enable RAG must be a boolean (True or False) but got {self.enable_rag} instead")

        if not isinstance(self.ui_dev_mode, bool):
            is_error = True
            logging.error(f"UI developer mode flag must be a boolean (True or False) but got {self.ui_dev_mode} instead")

        if is_error:
            raise RuntimeError(f"Invalid configuration received")


class YAMLPersonaParser(BaseYAMLParser):
    """ Parser for the agent persona file """

    root: str = "persona"
    key_species: str = "species"
    key_gender: str = "gender"
    key_intelligence: str = "intelligence-level"
    key_likes: str = "likes"
    key_dislikes: str = "dislikes"
    key_jobs: str = "jobs"
    key_traits: str = "traits"
    key_personality: str = "personality"
    key_hobbies: str = "hobbies"
    key_additional_languages: str = "additional-languages"
    key_relationships: str = "relationships"

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

    root: str = "scenario"
    key_base_setting: str = "base-setting"
    key_backgrounds: str = "backgrounds"
    key_actions: str = "actions"
    key_twists: str = "twists"

    def __init__(self, file_path: str | Path):
        super().__init__(file_path)
        # Since it shares same functionality with Persona parser, just inherit it

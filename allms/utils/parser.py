import pathlib

import yaml


class YAMLConfigFileParser:
    """ Parser for the user configuration file """

    key_ai_model: str = "model"
    key_reasoning_level: str = "reasoningLevel"
    key_max_agent_count: str = "maximumAgentCount"

    def __init__(self, file_path: str | pathlib.Path):
        self._file_path = pathlib.Path(file_path)
        assert self._file_path.exists(), f"Provided file: {file_path} doesn't exist. Make sure the path is correct"

        self.ai_model: str | None = None
        self.reasoning_level: str | None = None
        self.max_agent_count: int | None = None

    def parse(self) -> None:
        with open(self._file_path, "r") as f:
            yml_data = yaml.safe_load(f)

        expected_keys = [getattr(YAMLConfigFileParser, attr) for attr in dir(YAMLConfigFileParser) if attr.startswith("key_")]
        for ek in expected_keys:
            assert ek in yml_data, f"Expecting {ek} to be present in the config file but is missing. Did you edit it?"

        self.ai_model = yml_data[self.key_ai_model].lower()
        self.reasoning_level = yml_data[self.key_reasoning_level].lower()
        self.max_agent_count = yml_data[self.key_max_agent_count]

import random
from pathlib import Path
from typing import Optional, Type

from allms.config import AppConfiguration
from allms.utils.parser import BaseYAMLParser, YAMLNamesParser, YAMLPersonaParser, YAMLScenarioParser


class BaseGenerator:
    """ Base class for a persona/scenario generator """
    def __init__(self, file_dir: str | Path, file: str, parser_cls: Type[BaseYAMLParser], random_seed: int = None):
        self._file_path = Path(file_dir) / file
        self._parser = parser_cls(self._file_path)
        self._random_seed = random_seed

        assert self._file_path.exists(), f"File {self._file_path.name} does not exist in {file_dir}/"

        self.data = self._parser.parse()
        self._parser.validate(self.data)

        if random_seed is not None:
            assert isinstance(random_seed, int), f"Random seed must be a valid integer"
            random.seed(random_seed)

    def generate(self, *args, **kwargs) -> list[str]:
        """ Generate random personas/scenarios and return them """
        raise NotImplementedError

    @staticmethod
    def choose_from(choices: list[str], max_count: int = 1, is_random_count: bool = False) -> list[str]:
        """ Choose an item at random from the given list and return it """
        assert len(choices) >= max_count, f"Tried to sample {max_count} but list only has {len(choices)} items"
        count = max_count
        if is_random_count:
            count = random.choice(range(2, max_count+1))
        return random.sample(choices, count)


class PersonaGenerator(BaseGenerator):
    """ Class for randomly generating a persona """
    def __init__(self, genre: str = None):
        genre = genre if (genre is not None) else AppConfiguration.default_genre
        file_dir = AppConfiguration.resource_scenario_dir / genre
        super().__init__(file_dir=file_dir, file=AppConfiguration.resource_persona_yml, parser_cls=YAMLPersonaParser)

    def generate(self, n: int, max_choices: int = 4, *args, **kwargs) -> list[str]:
        """ Generate N random personas and returns them """

        backgrounds = self.data[YAMLPersonaParser.key_backgrounds]
        voices = self.data[YAMLPersonaParser.key_voices]
        characteristics = self.data[YAMLPersonaParser.key_characteristics]

        agent_backgrounds = self.choose_from(backgrounds, max_count=n)
        agent_voices = self.choose_from(voices, max_count=n)
        agent_personas = []

        def _join_items(_items: list[str]) -> str:
            """ Helper method to join the given items list """
            if len(_items) > 1:
                return ", ".join(_items[:-1]) + f" and {_items[-1]}"
            return _items[0]

        for agent_bg, agent_voice in zip(agent_backgrounds, agent_voices):
            agent_characteristics = self.choose_from(characteristics, max_choices, is_random_count=True)
            agent_character = _join_items(agent_characteristics)
            persona = f"{agent_bg} {agent_voice.capitalize()} {agent_character.capitalize()}."

            agent_personas.append(persona)

        return agent_personas


class ScenarioGenerator(BaseGenerator):
    """ Class for randomly generating a scenario """
    def __init__(self, genre: str = None):
        genre = genre if (genre is not None) else AppConfiguration.default_genre
        file_dir = AppConfiguration.resource_scenario_dir / genre
        super().__init__(file_dir=file_dir, file=AppConfiguration.resource_scenario_yml, parser_cls=YAMLScenarioParser)

    def generate(self, *args, **kwargs) -> list[str]:
        """ Generate a random scenario and returns it """
        scenarios: list[str] = self.data
        scenario = self.choose_from(scenarios)

        return scenario


class NameGenerator(BaseGenerator):
    """ Class for randomly generating a name """
    def __init__(self):
        file_dir = AppConfiguration.resource_names_dir
        super().__init__(file_dir=file_dir, file=AppConfiguration.resource_name_yml, parser_cls=YAMLNamesParser)

    def generate(self, n: int, *args, **kwargs) -> list[str]:
        """ Generate a list of random names and returns it """
        names: list[str] = self.data
        agent_names = self.choose_from(names, max_count=n)

        return agent_names

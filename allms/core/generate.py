import random
from pathlib import Path
from typing import Type

from allms.config import AppConfiguration
from allms.utils.parser import BaseYAMLParser, YAMLPersonaParser, YAMLScenarioParser


class BaseGenerator:
    """ Base class for a persona/scenario generator """
    def __init__(self, file_path: str | Path, parser_cls: Type[BaseYAMLParser], random_seed: int = None):
        self._file_path = file_path
        self._parser = parser_cls(self._file_path)
        self._random_seed = random_seed

        self.data = self._parser.parse()
        self._parser.validate(self.data)

        if random_seed is not None:
            assert isinstance(random_seed, int), f"Random seed must be a valid integer"
            random.seed(random_seed)

    def generate(self) -> str:
        """ Generate a random persona/scenario and return it """
        raise NotImplementedError

    @staticmethod
    def choose_from(choices: list[str], max_count: int = 1) -> str | list[str]:
        """ Choose an item at random from the given list and return it """
        if max_count > 1:
            assert len(choices) >= max_count, f"Tried to sample {max_count} but list only has {len(choices)} items"
            count = random.choice(range(1, max_count+1))
            return random.sample(choices, count)

        return random.choice(choices)


class PersonaGenerator(BaseGenerator):
    """ Class for randomly generating a persona """
    def __init__(self, max_choices: int = 4):
        super().__init__(file_path=AppConfiguration.resource_persona_path, parser_cls=YAMLPersonaParser)
        self._max_choices = max_choices
        self._relationships: list[str] = []
        self._age_range: list[str] = [str(i) for i in range(18, 101)]

    def generate(self) -> str:
        """ Generate a random persona and returns it """
        species = self.data[YAMLPersonaParser.key_species]
        genders = self.data[YAMLPersonaParser.key_gender]
        intelligence_levels = self.data[YAMLPersonaParser.key_intelligence]
        likes = self.data[YAMLPersonaParser.key_likes]
        dislikes = self.data[YAMLPersonaParser.key_dislikes]
        jobs = self.data[YAMLPersonaParser.key_jobs]
        traits = self.data[YAMLPersonaParser.key_traits]
        personalities = self.data[YAMLPersonaParser.key_personality]
        hobbies = self.data[YAMLPersonaParser.key_hobbies]
        languages = self.data[YAMLPersonaParser.key_additional_languages]
        relationships = self.data[YAMLPersonaParser.key_relationships]

        agent_species = self.choose_from(species)
        agent_gender = self.choose_from(genders)
        agent_age = self.choose_from(self._age_range)
        agent_intelligence = self.choose_from(intelligence_levels)
        agent_job = self.choose_from(jobs)

        # Following below can have >= 1 elements
        agent_likes: list[str] = self.choose_from(likes, max_count=self._max_choices)
        agent_dislikes: list[str] = self.choose_from(dislikes, max_count=self._max_choices)
        agent_traits: list[str] = self.choose_from(traits, max_count=self._max_choices)
        agent_personalities: list[str] = self.choose_from(personalities, max_count=self._max_choices)
        agent_hobbies: list[str] = self.choose_from(hobbies, max_count=self._max_choices)
        agent_languages: list[str] = ["English"] + self.choose_from(languages, max_count=self._max_choices)
        agent_relationships: list[str] = self.choose_from(relationships, max_count=self._max_choices)

        self._relationships = agent_relationships  # Save for later use

        def _join_items(_items: list[str]) -> str:
            """ Helper method to join the given items list """
            if len(_items) > 1:
                return ", ".join(_items[:-1]) + f" and {_items[-1]}"
            return _items[0]

        # Create the persona -- might turn out to be extremely weird but there are people like that (>_>)
        persona = f"A {agent_species} ({agent_age} years old) who identifies as {agent_gender} and is " + \
                  f"{agent_intelligence}. Currently employed as {agent_job}. Likes {_join_items(agent_likes)}. " + \
                  f"Dislikes {_join_items(agent_dislikes)}. Has the following traits -- " + \
                  f"{_join_items(agent_traits)} and is {_join_items(agent_personalities)}. Hobbies are " + \
                  f"{_join_items(agent_hobbies)}. Knows to read and write {_join_items(agent_languages)}."

        return persona

    def set_relationships(self, agent_ids: list[str]) -> str:
        """
        Set the relationship between the agent and the rest of the agents
        Returns the resulting persona string
        """
        # TODO: Implement this later on
        raise NotImplementedError


class ScenarioGenerator(BaseGenerator):
    """ Class for randomly generating a scenario """
    def __init__(self):
        super().__init__(file_path=AppConfiguration.resource_scenario_path, parser_cls=YAMLScenarioParser)

    def generate(self) -> str:
        """ Generate a random scenario and returns it """
        base_settings = self.data[YAMLScenarioParser.key_base_setting]
        backgrounds = self.data[YAMLScenarioParser.key_backgrounds]
        actions = self.data[YAMLScenarioParser.key_actions]
        twists = self.data[YAMLScenarioParser.key_twists]

        base_setting = self.choose_from(base_settings)
        background = self.choose_from(backgrounds)
        action = self.choose_from(actions)
        twist = self.choose_from(twists)

        scenario_pt_1 = f"{base_setting}, {background}".capitalize()
        scenario_pt_2 = f"{action}, {twist}".capitalize()
        scenario = f"{scenario_pt_1}. {scenario_pt_2}."

        return scenario

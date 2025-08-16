import logging
from pathlib import Path
from typing import Optional

from allms.config import AppConfiguration, RunTimeConfiguration
from allms.core.agents import Agent, AgentFactory
from allms.core.chat import ChatMessageHistory
from allms.core.generate import PersonaGenerator, ScenarioGenerator
from allms.core.log import GameEventLogs
from .state import GameState


class GameStateManager:
    """ Class for managing the game state """

    def __init__(self, config: RunTimeConfiguration):
        self._config = config
        self._logger = logging.getLogger(self.__class__.__name__)
        self._scenario_generator = ScenarioGenerator()
        self._persona_generator = PersonaGenerator()

        self._scenario: str = ""
        self._game_state: Optional[GameState] = None
        self._messages: Optional[ChatMessageHistory] = None
        self._event_logs: Optional[GameEventLogs] = None

    @property
    def scenario(self) -> str:
        return self._scenario

    def new(self) -> None:
        """ Creates a new game state """
        self._messages = ChatMessageHistory()
        self._event_logs = GameEventLogs()

        self._game_state = GameState(messages=self._messages, events=self._event_logs)
        self.update_scenario(self.generate_scenario())
        self.create_agents(self._config.default_agent_count)

    def load(self, file_path: str | Path) -> None:
        """ Loads the game state from the given path """
        # TODO: Implement the loading logic
        raise NotImplementedError

    def save(self, file_path: str | Path) -> None:
        """ Saves the game state to persistent storage """
        # TODO: Implement the saving logic
        raise NotImplementedError

    def create_agents(self, n_agents: int) -> None:
        """ Creates the agents and assigns them to the state """
        agents = AgentFactory.create(n_agents)
        self.__check_game_state_validity()

        self._game_state.initialize_agents(agents)

    def get_agent(self, agent_id: str) -> Agent:
        """ Returns the agent with the specified agent ID """
        return self._game_state.get_agent(agent_id)

    def get_all_agents(self) -> dict[str, Agent]:
        """ Returns the agents as a mapping between agent-ID and the agent object """
        return self._game_state.get_all_agents()

    def assign_agent_to_user(self, agent_id: str) -> None:
        """ Assigns the given agent to the user """
        self.__check_game_state_validity()
        self._game_state.assign_agent(agent_id)

    def generate_persona(self, agent_id: str, agent_ids: list[str]) -> str:
        """ Generates a new agent persona and returns it """
        persona = self._persona_generator.generate()
        persona = self._persona_generator.set_relationships(agent_id, agent_ids)
        return persona

    def generate_scenario(self) -> str:
        """ Generates a random scenario and returns it """
        scenario = self._scenario_generator.generate()
        return scenario

    def update_scenario(self, scenario: str) -> None:
        """ Updates the scenario with the given scenario """
        self.__check_game_state_validity()
        self._scenario = scenario
        self._game_state.initialize_scenario(scenario)

    def __check_game_state_validity(self) -> None:
        """ Helper method to check the validity of the game state """
        assert self._game_state is not None, f"Did you forget to instantiate game state first?"

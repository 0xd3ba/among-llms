import logging
from pathlib import Path
from typing import Optional

from allms.config import AppConfiguration, RunTimeConfiguration
from allms.core.agents import AgentFactory
from allms.core.chat import ChatMessageHistory
from allms.core.generate import ScenarioGenerator
from allms.core.log import GameEventLogs
from .state import GameState


class GameStateManager:
    """ Class for managing the game state """

    def __init__(self, config: RunTimeConfiguration):
        self._config = config
        self._logger = logging.getLogger(self.__class__.__name__)
        self._scenario_generator = ScenarioGenerator()

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
        self.randomize_scenario()
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

    def assign_agent_to_user(self, agent_id: str) -> None:
        """ Assigns the given agent to the user """
        self.__check_game_state_validity()
        self._game_state.assign_agent(agent_id)

    def randomize_scenario(self) -> None:
        """ Randomizes the scenario with a new one """
        self._scenario = self._scenario_generator.generate()
        self.__check_game_state_validity()

        self._game_state.initialize_scenario(self._scenario)

    def __check_game_state_validity(self) -> None:
        """ Helper method to check the validity of the game state """
        assert self._game_state is not None, f"Did you forget to instantiate game state first?"

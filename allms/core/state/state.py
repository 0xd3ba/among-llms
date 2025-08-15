from dataclasses import dataclass, field

from allms.core.agents import Agent
from allms.core.chat.history import ChatMessageHistory
from allms.core.log import GameEventLogs


@dataclass
class GameState:
    """ Class containing the latest state of the game """
    your_agent_id: str = ""              # The identifier of the agent assigned to you
    scenario: str = ""                   # The game scenario on which all the agents act on
    messages: ChatMessageHistory = None  # The history of the messages sent
    events: GameEventLogs = None         # The history of the game events (for debugging)
    start_time: int = 0                  # The start time of the game in UNIX milliseconds
    elapsed_duration: int = 0            # The elapsed duration in UNIX milliseconds

    game_paused: bool = True      # Set to true if the game is currently paused
    game_ended: bool = False      # Set to true if the game has ended, i.e. you got exposed
    game_won: bool = False        # Set to true if the game has ended and you won

    _all_agents: dict[str, Agent] = field(default_factory=dict)  # Mapping between agent ID and agent object
    _remaining_agent_ids: set[str] = field(default_factory=set)  # Set of all the remaining agent IDs in the game

    def initialize_scenario(self, scenario: str) -> None:
        """ Initializes the game scenario """
        self.scenario = scenario

    def initialize_agents(self, agents: list[Agent]) -> None:
        """ Initializes all the agents """
        self._all_agents.clear()
        self._remaining_agent_ids.clear()

        for agent in agents:
            agent_id = agent.id
            # Note: Each agent ID must be unique
            assert agent_id not in self._all_agents, f"Agent ID({agent_id}) already exists in the map"

            self._all_agents[agent_id] = agent
            self._remaining_agent_ids.add(agent_id)

    def assign_agent(self, agent_id: str) -> None:
        """ Assigns the given agent to the user """
        assert agent_id in self._all_agents, f"Your assigned agent ID({agent_id}) doesn't exist yet"
        self.your_agent_id = agent_id

    def get_agent(self, agent_id: str) -> Agent:
        """ Returns the agent specified by the provided agent ID """
        assert agent_id in self._all_agents, f"Trying to get agent ID({agent_id}) but it doesn't exist"
        return self._all_agents[agent_id]

    def remove_agent(self, agent_id: str) -> None:
        """ Removes the agent from the tracked agents """
        assert agent_id in self._remaining_agent_ids, f"Trying to remove agent ID({agent_id}) which is not present"
        self._remaining_agent_ids.remove(agent_id)

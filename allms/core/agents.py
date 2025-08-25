from collections import deque
from dataclasses import dataclass, field

from allms.config import AppConfiguration
from .generate import PersonaGenerator


@dataclass
class Agent:
    """ Class for an agent """
    id: str       # The unique identifier of the agent
    persona: str  # The persona assigned to the agent

    # List of message IDs of the messages sent by the agent
    msg_ids: set[str] = field(default_factory=set)

    # List of message IDs of the direct messages sent/received by the agent to/from other agents
    dm_msg_ids_recv: dict[str, set] = field(default_factory=dict)  # Mapping between agent ID and received msg id
    dm_msg_ids_sent: dict[str, set] = field(default_factory=dict)  # Mapping between agent ID and sent msg id

    # Maintain a rolling history of chat-logs of DMs, public messages and notifications
    chat_logs: deque[str] = field(default_factory=lambda: deque(maxlen=AppConfiguration.max_lookback_messages))

    def add_message_id(self, msg_id: str) -> None:
        """ Adds the message ID to the list of IDs sent by the agent """
        if msg_id not in self.msg_ids:
            self.msg_ids.add(msg_id)

    def add_dm_message_id(self, msg_id: str, agent_id: str, dm_received: bool) -> None:
        """ Adds the message id received (dm_received=True) or sent (dm_received=False) to the agent ID """
        dm_map = self.dm_msg_ids_recv if dm_received else self.dm_msg_ids_sent
        if agent_id not in dm_map:
            dm_map[agent_id] = set()
        dm_map[agent_id].add(msg_id)

    def add_to_chat_log(self, msg: str) -> None:
        """ Add the given message to the chat log """
        AppConfiguration.logger.log(f"Adding the following message to chat-log for agent({self.id}): {msg}")
        self.chat_logs.append(msg)

    def get_chat_logs(self) -> list[str]:
        return list(self.chat_logs)

    def get_message_ids(self, latest_first: bool = True) -> list[str]:
        """ Returns a sorted list of all the message IDs of the messages sent by the agent """
        msgs_list = sorted(list(self.msg_ids))
        if latest_first:
            msgs_list = msgs_list[::-1]
        return msgs_list

    def get_dm_message_ids(self, agent_id: str, dm_received: bool, latest_first: bool = True) -> list[str]:
        """
        Returns a sorted list of all the message IDs received (dm_received=True) or sent (dm_received=False)
        from/to the specified agent ID
        """
        dm_map = self.dm_msg_ids_recv if dm_received else self.dm_msg_ids_sent
        msg_ids = []

        if agent_id in dm_map:
            msg_ids = dm_map[agent_id]
            msg_ids = sorted(list(msg_ids))
            if latest_first:
                msg_ids = msg_ids[::-1]

        return msg_ids

    def get_persona(self) -> str:
        """ Returns the persona of the agent """
        return self.persona

    def update_persona(self, persona: str) -> None:
        """ Updates the persona of the agent with the provided one """
        self.persona = persona


class AgentFactory:
    """ Factory class for producing agents """
    @staticmethod
    def create(n_agents: int) -> list[Agent]:
        """ Creates N agents and returns them """
        min_count = AppConfiguration.min_agent_count
        assert n_agents >= min_count, f"Expected no. of agents to be >= {min_count} but received {n_agents} instead"

        agents = []
        persona_generator = PersonaGenerator()

        agent_ids = [AgentFactory.create_agent_id(i) for i in range(1, n_agents+1)]

        for agent_id in agent_ids:
            _ = persona_generator.generate()
            persona = persona_generator.set_relationships(agent_id, agent_ids)
            agent = Agent(id=agent_id, persona=persona)

            agents.append(agent)

        return agents

    @staticmethod
    def create_agent_id(i: int) -> str:
        """ Given an integer, returns the current agent ID """
        # Note: If you change this, make sure to change the comparator function below as well
        prefix = "Agent-"
        return f"{prefix}{i}"

    @staticmethod
    def agent_id_comparator(agent_id: str) -> int:
        """ Comparator for sorting agents to be used when sorting agent IDs """
        return int(agent_id.split("-")[-1])

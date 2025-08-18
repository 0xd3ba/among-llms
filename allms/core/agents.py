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

    def add_message_id(self, msg_id: str) -> None:
        """ Adds the message ID to the list of IDs sent by the agent """
        if msg_id not in self.msg_ids:
            self.msg_ids.add(msg_id)

    def get_message_ids(self, latest_first: bool = True) -> list[str]:
        """ Returns a sorted list of all the message IDs of the messages sent by the agent """
        msgs_list = sorted(list(self.msg_ids))
        if latest_first:
            msgs_list = msgs_list[::-1]
        return msgs_list

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

from collections import deque
from dataclasses import dataclass, field
from itertools import cycle, islice

from allms.config import AppConfiguration, RunTimeModel
from .generate import NameGenerator, PersonaGenerator


@dataclass
class Agent:
    """ Class for an agent """
    id: str               # The unique identifier of the agent
    persona: str          # The persona assigned to the agent
    model: RunTimeModel   # The AI model assigned to this agent which will be responsible for generating the responses
    max_lookback: int     # Length of context window for keeping track of messages/events/notifications

    # List of message IDs of the messages sent by the agent
    msg_ids: set[str] = field(default_factory=set)

    # List of message IDs of the direct messages sent/received by the agent to/from other agents
    dm_msg_ids_recv: dict[str, set] = field(default_factory=dict)  # Mapping between agent ID and received msg id
    dm_msg_ids_sent: dict[str, set] = field(default_factory=dict)  # Mapping between agent ID and sent msg id

    # Maintain a rolling history of chat-logs of DMs, public messages and notifications
    # Each item is of form (role, message/message_id, is_message_id)
    # Need to do it this way because if an agent modifies their message (edit/delete), it becomes difficult to update
    # the state in each and every chat log -- a better way is to just store the message IDs of all chat messages
    # and keep the notifications etc. as normal formatted messages. On every iteration, the LLM will fetch the latest
    # contents (even if edited/deleted) instead of stale version (if stored as formatted messages instead of IDs)
    _chat_logs: deque[tuple[str, str, bool]] = None
    _chat_context: deque[str] = None  # Also store the long-term context of the chat (used only by LLM)
    __latest_msg: str = ""  # Use as Producer/Consumer flags

    def __post_init__(self):
        if self._chat_logs is None:
            self._chat_logs = deque(maxlen=self.max_lookback)

        if self._chat_context is None:
            self._chat_context = deque(maxlen=self.max_lookback)

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

    def add_to_chat_log(self, role: str, msg: str, is_message_id: bool = False) -> None:
        """ Add the given message/message ID to the chat log """
        msg_type = "message ID" if is_message_id else "message"
        AppConfiguration.logger.log(f"Adding the following {msg_type} to chat-log for agent({self.id}): {msg}")
        self._chat_logs.append((role, msg, is_message_id))
        self.__latest_msg = msg  # Doesn't matter if it is an ID or a raw message

    def add_to_chat_context(self, context: str) -> None:
        """ Adds the given context to the long-term context """
        self._chat_context.append(context)

    def can_reply(self, latest_msg_id: str | None) -> bool:
        """ Returns True if the agent (LLM) is allowed to reply """
        return (latest_msg_id is None) or (self.__latest_msg != latest_msg_id)

    def get_chat_logs(self) -> list[tuple[str, str, bool]]:
        """ Returns the list of saved chat logs. Each item is of form (role, msg_id/msg, is_msg_id) """
        return list(self._chat_logs)

    def get_chat_context(self) -> str | None:
        """ Returns the latest long-term context (if present) else None """
        if self._chat_context:
            return self._chat_context[-1]
        return None

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

    def reset(self) -> None:
        """ Clears the chat messages and history logs """
        self.msg_ids.clear()
        self.dm_msg_ids_recv.clear()
        self.dm_msg_ids_sent.clear()
        self._chat_logs.clear()


class AgentFactory:
    """ Factory class for producing agents """
    @staticmethod
    def create(genre: str, n_agents: int, models: list[RunTimeModel], max_lookback: int) -> list[Agent]:
        """ Creates N agents and returns them """
        min_count = AppConfiguration.min_agent_count
        assert n_agents >= min_count, f"Expected no. of agents to be >= {min_count} but received {n_agents} instead"

        agents = []
        persona_generator = PersonaGenerator(genre)
        names_generator = NameGenerator()

        agent_ids = names_generator.generate(n=n_agents)
        assert len(agent_ids) == len(set(agent_ids)), f"Got duplicates in agent IDs list: {agent_ids}. This should not happen"

        personas = persona_generator.generate(n=n_agents)
        assigned_models = AgentFactory.__distribute_models(n_agents, models=models)

        for agent_id, persona, model in zip(agent_ids, personas, assigned_models):
            agent = Agent(id=agent_id, persona=persona, model=model, max_lookback=max_lookback)
            agents.append(agent)

        return agents

    @staticmethod
    def agent_id_comparator(agent_id: str) -> str:
        """ Comparator for sorting agents to be used when sorting agent IDs """
        return agent_id

    @staticmethod
    def __distribute_models(n_agents: int, models: list[RunTimeModel]) -> list[RunTimeModel]:
        """ Helper method to distribute the models equivalently across the agents """
        models_cycle = cycle(models)
        assigned_models = islice(models_cycle, n_agents)
        return list(assigned_models)

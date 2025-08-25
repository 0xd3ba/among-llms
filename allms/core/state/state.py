from collections import Counter
from dataclasses import dataclass, field

from allms.core.agents import Agent, AgentFactory
from allms.core.chat import ChatMessage, ChatMessageFormatter, ChatMessageHistory
from allms.core.log import GameEventLogs
from allms.core.vote import AgentVoting


@dataclass
class GameState:
    """ Class containing the latest state of the game """
    your_agent_id: str = ""       # The identifier of the agent assigned to you
    scenario: str = ""            # The game scenario on which all the agents act on
    start_time: int = 0           # The start time of the game in UNIX milliseconds
    elapsed_duration: int = 0     # The elapsed duration in UNIX milliseconds

    game_paused: bool = True      # Set to true if the game is currently paused
    game_ended: bool = False      # Set to true if the game has ended, i.e. you got exposed
    game_won: bool = False        # Set to true if the game has ended and you won

    messages: ChatMessageHistory = field(default_factory=ChatMessageHistory)  # History of the messages sent
    events: GameEventLogs = field(default_factory=GameEventLogs)              # History of the game events (for debugging)
    _all_agents: dict[str, Agent] = field(default_factory=dict)               # Mapping between agent ID and agent object
    _remaining_agent_ids: set[str] = field(default_factory=set)               # Set of all the remaining agent IDs in the game
    _voting: AgentVoting = field(default_factory=AgentVoting)                 # For handling voting

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

    def assign_agent_id_to_user(self, agent_id: str) -> None:
        """ Assigns the given agent to the user """
        assert agent_id in self._all_agents, f"Your assigned agent ID({agent_id}) doesn't exist yet"
        self.your_agent_id = agent_id

    def get_user_assigned_agent_id(self) -> str:
        """ Returns the user-assigned agent ID """
        agent_id = self.your_agent_id
        assert agent_id and agent_id in self._all_agents, \
            f"You have not been assigned an ID yet or it doesn't exist (id={agent_id})"
        return agent_id

    def get_agent(self, agent_id: str) -> Agent:
        """ Returns the agent specified by the provided agent ID """
        assert agent_id in self._all_agents, f"Trying to get agent ID({agent_id}) but it doesn't exist"
        return self._all_agents[agent_id]

    def get_all_agents(self) -> dict[str, Agent]:
        """ Returns a mapping of all agent IDs and the object """
        assert len(self._all_agents) > 0, f"Trying to get all the agents but there are no agents created yet"
        return self._all_agents

    def get_all_remaining_agents_ids(self) -> list[str]:
        """ Returns the list of all agent IDs """
        assert len(self._remaining_agent_ids) >= 2, f"There must be 2 agents left (you and a LLM) before the game " + \
            f"finishes but there are only {len(self._remaining_agent_ids)} in the list"
        remaining_ids = sorted(list(self._remaining_agent_ids), key=AgentFactory.agent_id_comparator)
        return remaining_ids

    def remove_agent(self, agent_id: str) -> None:
        """ Removes the agent from the tracked agents """
        assert agent_id in self._remaining_agent_ids, f"Trying to remove agent ID({agent_id}) which is not present"
        self._remaining_agent_ids.remove(agent_id)

    async def add_message(self, message: ChatMessage) -> None:
        """ Adds the given message to the message history log """
        # Check if the message is a reply to a previous message ID -- if yes, then the message must exist
        if message.reply_to_id is not None:
            assert self.messages.exists(message.reply_to_id), f"Trying to reply to a message ID " + \
                f"({message.reply_to_id}) which does not exist in the history"

        await self.messages.add(message)

        # Update the list of message IDs sent by the agent
        agent_id = message.sent_by
        assert agent_id in self._remaining_agent_ids, f"Agent({agent_id}) is trying to send a message but is not in" + \
            f" the set of (remaining) agents: {self._remaining_agent_ids}"

        agent_from = self.get_agent(agent_id)
        agent_from.add_message_id(message.id)
        agent_from.add_to_chat_log(ChatMessageFormatter.format_to_string(message))

        # Now check if the message is a DM (sent_to is not None)
        sent_to = message.sent_to
        if sent_to is not None:
            agent_to = self.get_agent(sent_to)
            agent_from.add_dm_message_id(msg_id=message.id, agent_id=agent_to.id, dm_received=False)  # Sent a DM
            agent_to.add_dm_message_id(msg_id=message.id, agent_id=agent_id, dm_received=True)  # Received a DM

    def get_message(self, message_id: str) -> ChatMessage:
        """ Fetches the message with the given message ID and returns it """
        return self.messages.get(message_id)

    def get_messages_sent_by(self, agent_id: str, latest_first: bool = True) -> list[ChatMessage]:
        """ Fetches all the messages sent by agent ID and returns it """
        assert agent_id in self._remaining_agent_ids, f"Trying to fetch messages by agent ID({agent_id}) which is not present"
        agent = self._all_agents[agent_id]
        all_msg_ids = agent.get_message_ids(latest_first=latest_first)
        all_msgs = [self.messages.get(msg_id) for msg_id in all_msg_ids]

        return all_msgs

    async def edit_message(self, msg_id: str, msg_contents: str, edited_by_you: bool) -> None:
        """ Edits the message with the given message ID """
        await self.messages.edit(msg_id, msg_contents, edited_by_you)
        if edited_by_you:
            self.__check_and_notify_if_modifying_others_message(msg_id, is_edit=True)

    async def delete_message(self, msg_id, deleted_by_you) -> None:
        """ Deletes the message with the given message ID """
        await self.messages.delete(msg_id, deleted_by_you)
        if deleted_by_you:
            self.__check_and_notify_if_modifying_others_message(msg_id, is_edit=False)

    def start_voting(self) -> None:
        """ Starts the voting process """
        self._voting.start_vote()

    def vote(self, by_agent: str, for_agent: str) -> None:
        assert by_agent in self._remaining_agent_ids, f"{by_agent} is trying to vote but is not in the remaining agents list"
        assert for_agent in self._remaining_agent_ids, f"{by_agent} is voting for {for_agent} who is not in the remaining agents list"
        self._voting.vote(by_agent, for_agent)

    def end_voting(self) -> Counter:
        """ Stops the voting process and returns the results """
        return self._voting.end_vote()

    def __check_and_notify_if_modifying_others_message(self, msg_id: str, is_edit: bool = True) -> None:
        """ Helper method to check if modifying other's message """
        your_id = self.your_agent_id
        msg = self.get_message(msg_id)

        if msg.sent_by == your_id:
            return

        # Modifying someone else's message
        # Send them a notification about the modification
        # Note: is_edit=False implies deleting their message
        tgt_agent = self.get_agent(msg.sent_by)
        fmt_msg = ChatMessageFormatter.create_hacked_by_human_message(msg, is_edit=is_edit)
        tgt_agent.add_to_chat_log(fmt_msg)

from __future__ import annotations
import logging
from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Optional

from allms.config import AppConfiguration
from allms.core.agents import Agent, AgentFactory
from allms.core.chat import ChatMessage, ChatMessageFormatter, ChatMessageHistory, ChatMessageIDGenerator
from allms.core.llm.roles import LLMRoles
from allms.core.log import GameEventLogs
from allms.core.vote import AgentVoting


@dataclass
class GameState:
    """ Class containing the latest state of the game """
    your_agent_id: str = ""                      # The identifier of the agent assigned to you
    genre: str = AppConfiguration.default_genre  # The genre of the scenario and personas
    scenario: str = ""                           # The game scenario on which all the agents act on
    start_time: int = 0                          # The start time of the game in UNIX milliseconds
    elapsed_duration: int = 0                    # The elapsed duration in UNIX milliseconds

    game_paused: bool = True      # Set to true if the game is currently paused
    game_ended: bool = False      # Set to true if the game has ended, i.e. you got exposed
    game_won: bool = False        # Set to true if the game has ended and you won

    messages: ChatMessageHistory = field(default_factory=ChatMessageHistory)  # History of the messages sent
    events: GameEventLogs = field(default_factory=GameEventLogs)              # History of the game events (for debugging)
    _all_agents: dict[str, Agent] = field(default_factory=dict)               # Mapping between agent ID and agent object
    _remaining_agent_ids: set[str] = field(default_factory=set)               # Set of all the remaining agent IDs in the game
    _voting: AgentVoting = field(default_factory=AgentVoting)                 # For handling voting
    _id_generator: ChatMessageIDGenerator = field(default_factory=ChatMessageIDGenerator)

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

    def reset(self) -> None:
        """ Resets the game state to the beginning (everything except the scenario and agent IDs and personas) """
        self.start_time = 0
        self.elapsed_duration = 0
        self.game_paused = True
        self.game_ended = False
        self.game_won = False
        self.messages.reset()
        self.events.reset()
        self._remaining_agent_ids.clear()
        self._voting.reset()
        self._id_generator = ChatMessageIDGenerator()

        for agent_id in self._all_agents:
            agent = self._all_agents[agent_id]
            agent.reset()
            self._remaining_agent_ids.add(agent_id)

    def get_genre(self) -> str:
        """ Returns the currently set genre """
        return self.genre

    def get_scenario(self) -> str:
        """ Returns the scenario """
        return self.scenario

    def get_game_won(self) -> bool:
        """ Returns True if the game was won, False otherwise """
        return self.game_won

    def get_game_ended(self) -> bool:
        """ Returns True if the game has ended, False otherwise """
        return self.game_ended

    def update_genre(self, genre: str) -> None:
        """ Updates the currently set genre with new genre """
        self.genre = genre

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

    def get_number_of_remaining_agents(self) -> int:
        """ Returns the count of the remaining agents """
        return len(self._remaining_agent_ids)

    def remove_agent(self, agent_id: str) -> None:
        """ Removes the agent from the tracked agents """
        assert agent_id in self._remaining_agent_ids, f"Trying to remove agent ID({agent_id}) which is not present"
        self._remaining_agent_ids.remove(agent_id)

    def get_start_time(self) -> int:
        """ Returns the start time (in UNIX milliseconds) """
        return self.start_time

    def update_start_time(self, start_timestamp_ms: int) -> None:
        """ Sets the start time (in UNIX milliseconds) """
        assert isinstance(start_timestamp_ms, int) and start_timestamp_ms > 0, f"Expecting start time to be a positive integer"
        self.start_time = start_timestamp_ms

    def get_duration(self) -> int:
        """ Returns the elapsed duration (in UNIX milliseconds) """
        return self.elapsed_duration

    def set_duration(self, duration_ms: int) -> None:
        """ Sets the duration to the given value """
        assert isinstance(duration_ms, int) and duration_ms > 0, f"Expected duration to be a UNIX millisecond but got {duration_ms} instead"
        self.elapsed_duration = duration_ms

    def update_duration(self, curr_timestamp_ms: int) -> None:
        """ Updates the duration (in milliseconds) since the start. Expects timestamp to be a UNIX millisecond """
        assert isinstance(curr_timestamp_ms, int) and curr_timestamp_ms > 0, f"Expecting timestamp to be a positive integer"
        assert curr_timestamp_ms >= self.start_time, f"Current timestamp ({curr_timestamp_ms}) < start timestamp ({self.start_time})"
        self.elapsed_duration = curr_timestamp_ms - self.start_time

    def generate_message_id(self) -> str:
        return self._id_generator.next()

    async def add_event(self, msg: ChatMessage) -> None:
        """ Adds the announcement message """
        await self.messages.add(msg)

    async def add_message(self, message: ChatMessage) -> None:
        """ Adds the given message to the message history log """
        # Check if the message is a reply to a previous message ID -- if yes, then the message must exist
        if message.reply_to_id is not None:
            assert self.messages.exists(message.reply_to_id), f"Trying to reply to a message ID " + \
                f"({message.reply_to_id}) which does not exist in the history"

        # Update the list of message IDs sent by the agent
        agent_id = message.sent_by
        if agent_id not in self._remaining_agent_ids:
            AppConfiguration.logger.log(
                f"Agent({agent_id}) is trying to send a message but is not in " +
                f"the set of (remaining) agents: {self._remaining_agent_ids}"
            )
            return

        await self.messages.add(message)

        agent_from = self.get_agent(agent_id)
        agent_from.add_message_id(message.id)

        broadcast_msg_to = {agent_id}

        # The message was sent by you via a different agent -- notify the agent in their logs
        if (agent_id != self.your_agent_id) and message.sent_by_you:
            agent_from.add_to_chat_log(LLMRoles.system, ChatMessageFormatter.create_sent_by_human_message(message))

        # If agent suspects someone, add it to their chat log
        if not message.sent_by_you and (message.suspect is not None):
            agent_from.add_to_chat_log(LLMRoles.system, ChatMessageFormatter.create_suspicion_message(message))

        # Now check if the message is a DM (sent_to is not None)
        sent_to = message.sent_to
        if sent_to is not None:
            broadcast_msg_to.add(sent_to)
            agent_to = self.get_agent(sent_to)
            agent_from.add_dm_message_id(msg_id=message.id, agent_id=agent_to.id, dm_received=False)  # Sent a DM
            agent_to.add_dm_message_id(msg_id=message.id, agent_id=agent_id, dm_received=True)  # Received a DM
        else:  # Sending to everyone
            broadcast_msg_to.update(self._remaining_agent_ids)

        for aid in broadcast_msg_to:
            role = LLMRoles.assistant if (aid == agent_id) else LLMRoles.user
            self._all_agents[aid].add_to_chat_log(role, message.id, is_message_id=True)

    def get_message(self, message_id: str) -> ChatMessage:
        """ Fetches the message with the given message ID and returns it """
        return self.messages.get(message_id)

    def get_messages_sent_by(self, agent_id: str, latest_first: bool = True) -> list[ChatMessage]:
        """ Fetches all the messages sent by agent ID and returns it """
        assert agent_id in self._all_agents, f"Trying to fetch messages by agent ID({agent_id}) which is not present"
        agent = self._all_agents[agent_id]
        all_msg_ids = agent.get_message_ids(latest_first=latest_first)
        all_msgs = [self.messages.get(msg_id) for msg_id in all_msg_ids]

        return all_msgs

    def get_all_messages(self, ids_only: bool = False) -> list[ChatMessage] | list[str]:
        """ Fetches all the chat messages or message IDs stored in the history and returns them """
        return self.messages.get_all(ids_only)

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

    async def announce_to_agents(self, msg: ChatMessage) -> None:
        """
        Broadcasts the given message to the intended recipients (if None, broadcasts to all remaining agents)
        Note: Use this method to only announce those messages that you want to be visible in the exported chat
        """
        agent_ids = msg.sent_to

        if agent_ids is None:
            agent_ids = self.get_all_remaining_agents_ids()
        elif isinstance(agent_ids, str):
            agent_ids = [agent_ids]

        await self.messages.add(msg)  # Also store it in the history, so that exported chats include this announcement

        AppConfiguration.logger.log(f"Announcing to {agent_ids} ... ")

        fmt_msg = ChatMessageFormatter.create_announcement_message(msg=msg)
        for agent_id in agent_ids:
            self._all_agents[agent_id].add_to_chat_log(role=LLMRoles.system, msg=fmt_msg)

    def voting_has_started(self) -> tuple[bool, Optional[str]]:
        """ Returns (True, agent_id_who_started_it) if voting has started. (False, None) otherwise """
        return self._voting.voting_has_started()

    def get_total_voters(self) -> int:
        """ Returns the total number of voters who voted so far """
        return self._voting.total_voters()

    def start_voting(self, started_by: str) -> bool:
        """ Starts the voting process. Returns True if started. False otherwise """
        if self.voting_has_started()[0]:
            AppConfiguration.logger.log(f"Trying to start a vote by {started_by} when it's already started. Ignoring.")
            return False
        self._voting.start_vote(started_by=started_by)
        return True

    def vote(self, by_agent: str, for_agent: str) -> bool:
        """ Vote for a specific agent by the given agent. Returns True if agent could vote. False otherwise """
        if by_agent not in self._remaining_agent_ids:
            AppConfiguration.logger.log(f"{by_agent} is trying to vote but is not in the remaining agents list", level=logging.CRITICAL)
            return False
        elif for_agent not in self._remaining_agent_ids:
            AppConfiguration.logger.log(f"{by_agent} is voting for {for_agent} who is not in the remaining agents list", level=logging.CRITICAL)
            return False
        else:
            return self._voting.vote(by_agent, for_agent)

    def get_voted_for_who(self, by_agent: str) -> Optional[str]:
        """ Returns the ID of the agent that the given agent voted for (if any), else None """
        return self._voting.get_voted_for_who(by_agent)

    def can_vote(self, agent_id: str) -> bool:
        """ Returns True if the agent is allowed to vote """
        return self._voting.can_vote(by_agent=agent_id)

    def end_voting(self) -> tuple[Optional[Counter], Optional[list[tuple[str, str]]]]:
        """ Stops the voting process and returns the results """
        if self.voting_has_started()[0]:
            vote_list = self._voting.get_who_voted_and_for_whom()
            return self._voting.end_vote(), vote_list

        # Vote already ended -- nothing to do
        AppConfiguration.logger.log(f"Trying to end a vote when it has already ended. Ignoring.")
        return None, None

    def end_game(self, won: bool) -> None:
        self.game_ended = True
        self.game_won = won
        # TODO: Compute the game duration

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
        tgt_agent.add_to_chat_log(LLMRoles.system, fmt_msg)

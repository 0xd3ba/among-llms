import asyncio
import json
import logging
import math
import random
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from typing import Any, Callable, Optional

from allms.cli.callbacks import ChatCallbackType, ChatCallbacks
from allms.config import AppConfiguration, RunTimeConfiguration
from allms.core.agents import Agent, AgentFactory
from allms.core.chat import ChatMessage, ChatMessageHistory, ChatMessageIDGenerator, ChatMessageFormatter
from allms.core.generate import PersonaGenerator, ScenarioGenerator
from allms.core.log import GameEventLogs
from allms.core.llm.loop import ChatLoop
from allms.utils.save import SavingUtils
from .callbacks import StateManagerCallbackType, StateManagerCallbacks
from .state import GameState


class GameStateManager:
    """ Class for managing the game state """

    def __init__(self, config: RunTimeConfiguration):
        self._config = config
        self._logger = AppConfiguration.logger
        self._msg_id_generator = ChatMessageIDGenerator()
        self._valid_genres = self.get_available_genres()
        self._scenario_generator = ScenarioGenerator()
        self._persona_generator = PersonaGenerator()

        self._scenario: str = ""
        self._game_state: Optional[GameState] = None
        self._on_new_message_lock: asyncio.Lock = asyncio.Lock()  # To ensure one update at a time
        self._on_new_message_callback: Optional[Callable] = None

        self._vote_started_timestamp: Optional[int] = None
        self._vote_will_end_on_timestamp: Optional[int] = None

        self._chat_callbacks: Optional[ChatCallbacks] = None
        self._self_callbacks: StateManagerCallbacks = StateManagerCallbacks(self.__generate_callbacks())
        self._chat_loop: Optional[ChatLoop] = None

    async def new(self) -> None:
        """ Creates a new game state """
        self._logger.log("Creating a new game state ...")
        self._game_state = GameState()
        self.update_scenario(self.generate_scenario())
        self.create_agents(self._config.default_agent_count)

        await self._game_state.messages.initialize()

    def load(self, file_path: str | Path) -> None:
        """ Loads the game state from the given path """
        # TODO: Implement the loading logic
        raise NotImplementedError

    def save(self) -> Optional[Path]:
        """ Saves the game state to persistent storage and returns the path of stored location """
        # Will be saved inside root_dir/timestamp/*
        save_file_game_state = "game_state.json"
        save_file_chat_msgs = "chat.txt"
        clock = AppConfiguration.clock
        logger = AppConfiguration.logger

        curr_ts = clock.current_timestamp_in_iso_format()
        curr_ts = clock.convert_to_snake_case(curr_ts)

        root_dir = Path(self._config.save_directory)
        save_dir = root_dir / curr_ts

        try:
            save_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.log(f"Exception while creating save directory ({save_dir.resolve()}): {e} ")
            return None

        with open(save_dir/save_file_game_state, "w", encoding="utf-8") as f:
            game_state = asdict(self._game_state)
            game_state = SavingUtils.properly_serialize_json(game_state)
            json_string = json.dumps(game_state, indent=4)
            f.write(json_string)

        # TODO: Need to save the message ID generator class

        # Export the chat logs in human-readable format
        messages = self.__export_chat()
        n_messages = len(messages)

        with open(save_dir/save_file_chat_msgs, "w", encoding="utf-8") as f:
            for i, msg in enumerate(messages):
                f.write(msg)
                f.write("\n" if (i != n_messages-1) else "")

        return save_dir

    def start_llms(self) -> None:
        """ Method to start the chatroom """
        if self._config.ui_dev_mode:
            return

        your_id = self.get_user_assigned_agent_id()
        self._logger.log(f"You have been assigned as  {your_id}")
        self._chat_loop = ChatLoop(config=self._config,
                                   your_agent_id=your_id,
                                   agents=self.get_all_agents(),
                                   scenario=self.get_scenario(),
                                   callbacks=self._self_callbacks
                                   )
        # TODO: Handle any pre-processing steps, if any, that might need to be done before loop starts
        self._chat_loop.start()

    def pause_llms(self) -> None:
        """ Method to pause the chatroom """
        if self._chat_loop is not None:
            self._chat_loop.pause()

    def stop_llms(self, agent_id: str = None) -> None:
        """ Method to stop all the chatroom LLMs (agent_id = None) or a specific agent's LLM (agent_id) """
        if self._chat_loop is None:
            llm_for = "all LLMs" if (agent_id is None) else f"LLM for {agent_id}"
            self._logger.log(f"Trying to stop {llm_for} when there is no chat loop running", level=logging.WARNING)
            return

        if agent_id is None:
            # TODO: Ensure all agents are stopped before resetting everything
            self._chat_loop.stop()
            self._chat_loop = None
        else:
            self._chat_loop.stop_agents(agent_id)

    def register_chat_callbacks(self, callbacks: ChatCallbacks) -> None:
        """ Registers the chat callbacks """
        self._chat_callbacks = callbacks

    def get_scenario(self) -> str:
        """ Returns the current scenario """
        return self._scenario

    def get_game_won(self) -> bool:
        """ Returns if the game has been won """
        return self._game_state.get_game_won()

    def create_agents(self, n_agents: int) -> None:
        """ Creates the agents and assigns them to the state """
        genre = self.get_genre()
        self._logger.log(f"Creating {n_agents} agents for given the genre: '{genre}' ...")
        agents = AgentFactory.create(genre=genre, n_agents=n_agents)
        self.__check_game_state_validity()

        self._game_state.initialize_agents(agents)

    def get_agent(self, agent_id: str) -> Agent:
        """ Returns the agent with the specified agent ID """
        self.__check_game_state_validity()
        return self._game_state.get_agent(agent_id)

    def get_all_agents(self) -> dict[str, Agent]:
        """ Returns the agents as a mapping between agent-ID and the agent object """
        self.__check_game_state_validity()
        return self._game_state.get_all_agents()

    def get_all_remaining_agents_ids(self) -> list[str]:
        """ Returns all the IDs of the agents that are remaining """
        self.__check_game_state_validity()
        return self._game_state.get_all_remaining_agents_ids()

    def pick_random_agent_id(self) -> str:
        """ Picks an agent at random and returns its ID """
        self.__check_game_state_validity()
        agent_ids = self.get_all_agents().keys()
        return random.choice(list(agent_ids))

    def assign_agent_to_user(self, agent_id: str) -> None:
        """ Assigns the given agent to the user """
        self.__check_game_state_validity()
        self._game_state.assign_agent_id_to_user(agent_id)

    def get_user_assigned_agent_id(self) -> str:
        """ Returns the agent ID assigned to the user """
        self.__check_game_state_validity()
        return self._game_state.get_user_assigned_agent_id()

    def get_available_genres(self) -> set[str]:
        """ Returns the list of available genres """
        genres = {genre.name for genre in AppConfiguration.resource_scenario_dir.glob("*") if genre.is_dir()}
        return genres

    def get_genre(self) -> str:
        """ Returns the currently set genre """
        return self._game_state.get_genre()

    def generate_persona(self) -> str:
        """
        Generates a new agent persona (based on the currently set genre) and returns it
        Note: Might generate a duplicate persona
        """
        self.__check_game_state_validity()
        persona = self._persona_generator.generate(n=1)
        return persona[0]

    def generate_scenario(self) -> str:
        """ Generates a random scenario (based on currently set genre) and returns it """
        self.__check_game_state_validity()
        scenario = self._scenario_generator.generate()
        return scenario[0]

    def update_genre(self, genre: str) -> None:
        """ Updates the genre """
        self.__check_game_state_validity()
        self.__check_genre_validity(genre)

        curr_genre = self._game_state.get_genre()
        if genre != curr_genre:
            self._logger.log(f"Updating genre to '{genre}' ...")
            self._game_state.update_genre(genre)
            self._scenario_generator = ScenarioGenerator(genre)
            self._persona_generator = PersonaGenerator(genre)

    def update_scenario(self, scenario: str) -> None:
        """ Updates the scenario with the given scenario """
        self.__check_game_state_validity()
        self._scenario = scenario
        self._logger.log(f"Updating scenario to '{scenario}' ...")
        self._game_state.initialize_scenario(scenario)

    async def send_message(self,
                           msg: str,
                           sent_by: str,
                           sent_by_you: bool,
                           sent_to: Optional[str],
                           thought_process: str = "",
                           reply_to_id: Optional[str] = None,
                           suspect_id: Optional[str] = None,
                           suspect_confidence: Optional[int] = None,
                           suspect_reason: Optional[str] = None
                           ) -> str:
        """ Sends a message by the given agent ID and returns the message ID """
        self.__check_game_state_validity()
        msg = self.__create_new_message(msg=msg, sent_by=sent_by, sent_by_you=sent_by_you, sent_to=sent_to,
                                        thought_process=thought_process, reply_to_id=reply_to_id, suspect_id=suspect_id,
                                        suspect_reason=suspect_reason, suspect_confidence=suspect_confidence)
        await self._game_state.add_message(msg)
        return msg.id

    def get_message(self, msg_id: str) -> ChatMessage:
        """ Returns the message associated with the given message ID """
        self.__check_game_state_validity()
        return self._game_state.get_message(msg_id)

    def get_messages_sent_by(self, agent_id: str) -> list[ChatMessage]:
        """ Returns the list of messages sent by the specified agent id """
        self.__check_game_state_validity()
        return self._game_state.get_messages_sent_by(agent_id, latest_first=True)

    async def edit_message(self, msg_id: str, msg_contents: str, edited_by_you: bool) -> None:
        """ Edits the message with the given message ID """
        await self._game_state.edit_message(msg_id, msg_contents, edited_by_you)

    async def delete_message(self, msg_id: str, deleted_by_you: bool) -> None:
        """ Deletes the message with the given message ID """
        await self._game_state.delete_message(msg_id, deleted_by_you)

    def announce_to_agents(self, inform_msg: str, announce_to: str = None) -> None:
        """ Announces the given message to the specified agent or all the agents (announce_to=None) """
        msg = self.__create_new_message(msg=inform_msg, sent_to=announce_to, is_announcement=True)
        self._game_state.announce_to_agents(msg)

    def voting_has_started(self) -> tuple[bool, Optional[str]]:
        """ Method that returns (True, agent_id_who_started_it) if voting has started. (False, None) otherwise """
        return self._game_state.voting_has_started()

    def start_vote(self, started_by: str, started_by_you: bool = False) -> None:
        """ Method to start the voting process """
        started = self._game_state.start_voting(started_by=started_by)
        if not started:
            return

        your_agent_id = self.get_user_assigned_agent_id()
        need_to_inform = True if (started_by_you and (started_by != your_agent_id)) else False

        if need_to_inform:
            # Inform the agent that it was you (the human) who started the vote on their behalf
            self._logger.log(f"Informing {started_by} that you have started the vote as them ...")
            inform_msg = "The human has started the vote as you"
            self.announce_to_agents(inform_msg, announce_to=started_by)

        # New voting has been started -- track the timestamp
        # Need this to ensure vote ends after pre-specified amount of time
        curr_ts = AppConfiguration.clock.current_timestamp_in_milliseconds_utc()
        vote_duration_min = AppConfiguration.max_vote_duration_min
        end_ts = AppConfiguration.clock.add_n_minutes(curr_ts, n_minutes=vote_duration_min)

        # Update the UI that a vote has started
        self.__invoke_chat_callback(ChatCallbackType.VOTE_HAS_STARTED, started_by=started_by)

        self._vote_started_timestamp = curr_ts
        self._vote_will_end_on_timestamp = end_ts
        self._logger.log(f"Voting will end on {AppConfiguration.clock.milliseconds_to_iso_format(end_ts)}")
        # TODO: Update the UI with a message / toast

    def can_vote(self, agent_id: str) -> bool:
        """ Returns True if the given agent is allowed to vote, else False"""
        return self._game_state.can_vote(agent_id)

    def end_vote(self) -> None:
        """ Method to end the voting process """
        results, vote_list = self._game_state.end_voting()
        if results is None:
            return

        kick_agent_id, vote_conclusion = self.__process_vote_results(results, vote_list)
        self._logger.log(f"Result: {vote_conclusion}")

        # Inform agents in their chat-logs that voting has ended, who got how many votes, who got kicked out etc.
        self.announce_to_agents(inform_msg=vote_conclusion)
        # Update the UI with a message that the vote has concluded
        self.__invoke_chat_callback(ChatCallbackType.VOTE_HAS_ENDED, conclusion=vote_conclusion)

        if kick_agent_id is not None:
            self.terminate_agent(kick_agent_id)

        # Reset the timestamps to None
        self._vote_started_timestamp = None
        self._vote_will_end_on_timestamp = None

    def vote(self, by_agent: str, for_agent: str, voting_by_you: bool = False) -> None:
        """ Method to participate in the vote """
        could_vote = self._game_state.vote(by_agent, for_agent)
        if not could_vote:
            return

        your_agent_id = self.get_user_assigned_agent_id()
        need_to_inform = True if (voting_by_you and (by_agent != your_agent_id)) else False

        if need_to_inform:
            # Inform the agent that it was you (the human) who did the vote on their behalf
            self._logger.log(f"Informing {by_agent} that you have voted for {for_agent} as them ...")
            inform_msg = f"The human has voted for <{for_agent}> as you"
            self.announce_to_agents(inform_msg=inform_msg, announce_to=by_agent)

        # Check if this was the last agent to vote -- if yes, we can end the vote and arrive at a conclusion
        total_voters_so_far = self._game_state.get_total_voters()
        n_agents_remaining = self._game_state.get_number_of_remaining_agents()
        assert total_voters_so_far <= n_agents_remaining, (
            f"Total voters ({total_voters_so_far}) > number of agents remaining ({n_agents_remaining}). " +
            f"This should not happen."
        )

        if total_voters_so_far == n_agents_remaining:
            self.end_vote()

    def get_voted_for_who(self, by_agent: str) -> Optional[str]:
        """ Returns the ID of the agent that the given agent voted for (if any), else None """
        return self._game_state.get_voted_for_who(by_agent)

    def terminate_agent(self, agent_id: str) -> None:
        """ Terminates the agent with the given ID """
        your_id = self.get_user_assigned_agent_id()
        n_remaining = self._game_state.get_number_of_remaining_agents()
        won = (n_remaining == 3) and (agent_id != your_id)  # n == 3 because we have not removed the agent yet

        self._game_state.remove_agent(agent_id)
        self._logger.log(f"{agent_id} terminated", level=logging.CRITICAL)

        # Stop the LLM associated with this agent
        if (agent_id != your_id) and (not won):
            self.stop_llms(agent_id)

            # Inform the LLMs in their logs that this was not the human
            inform_msg = f"{agent_id} has been TERMINATED. {agent_id} was NOT the HUMAN ..."
            self._logger.log(f"Announcing the following to all the LLMs: {inform_msg}")
            self.announce_to_agents(inform_msg=inform_msg)

            # Update the selection list in the UI to not include this agent
            self.__invoke_chat_callback(ChatCallbackType.UPDATE_AGENTS_LIST)

        # You got caught, or you won -- either ways, the game has ended
        else:
            self.stop_llms()
            self.end_game(won)

    def end_game(self, won: bool) -> None:
        """ Method that stops the game """
        # TODO: Show game ended screen on the UI
        self._game_state.end_game(won)
        self.__invoke_chat_callback(ChatCallbackType.TERMINATE_ALL_TASKS)
        self.__invoke_chat_callback(ChatCallbackType.GAME_HAS_ENDED, won)

    async def background_worker(self) -> None:
        """ Worker that runs in background checking for voting status, tracking duration etc. """
        clock = AppConfiguration.clock

        self._logger.log(f"Starting worker in the the background ...")
        start_ts = clock.current_timestamp_in_milliseconds_utc()
        self._game_state.update_start_time(start_ts)

        try:
            while True:
                await asyncio.sleep(1)  # Give control to others
                curr_ts = clock.current_timestamp_in_milliseconds_utc()
                self._game_state.update_duration(curr_ts)

                # Check the voting status
                if self._vote_started_timestamp is not None:
                    if curr_ts >= self._vote_will_end_on_timestamp:
                        self._logger.log(f"Ending vote due to duration timeout ...")
                        self.end_vote()

        except (asyncio.CancelledError, Exception) as e:
            self._logger.log(f"Received termination signal for background worker", level=logging.CRITICAL)

        duration = self._game_state.get_duration()
        duration, duration_unit = clock.calculate_duration(duration_ms=duration)
        self._logger.log(f"Stopping background worker")
        self._logger.log(f"Elapsed chatroom duration: {duration} {duration_unit}")

    def __create_new_message(self,
                             msg: str,
                             sent_by: str = None,
                             sent_by_you: bool = False,
                             sent_to: Optional[str] = None,
                             thought_process: str = "",
                             reply_to_id: Optional[str] = None,
                             suspect_id: Optional[str] = None,
                             suspect_confidence: Optional[int] = None,
                             suspect_reason: Optional[str] = None,
                             is_announcement: bool = False
                             ) -> ChatMessage:
        """ Helper method to create a message and return it """
        msg_id = self._msg_id_generator.next()
        timestamp = AppConfiguration.clock.current_timestamp_in_iso_format()

        # If the message is an announcement message, overwrite the sent_by parameter
        # Didn't think yet what would be an appropriate sent_by name or how it will be displayed in exported chats
        # but for now, let's leave it as "System"
        if is_announcement:
            sent_by = "System"
        else:
            assert sent_by is not None, f"sent_by is None while creating a message that is not an announcement"

        chat_msg = ChatMessage(id=msg_id, timestamp=timestamp, msg=msg, sent_by=sent_by, sent_by_you=sent_by_you,
                               sent_to=sent_to, thought_process=thought_process, reply_to_id=reply_to_id,
                               suspect=suspect_id, suspect_reason=suspect_reason, suspect_confidence=suspect_confidence,
                               is_announcement=is_announcement)
        return chat_msg

    def __check_game_state_validity(self) -> None:
        """ Helper method to check the validity of the game state """
        assert self._game_state is not None, f"Did you forget to instantiate game state first?"

    def __check_genre_validity(self, genre: str) -> None:
        """ Helper method to check if the given genre is valid """
        assert genre in self._valid_genres, f"Given genre({genre}) is not supported. Valid genres: {self._valid_genres}"

    def __process_vote_results(self, results: Counter, vote_list: list[tuple[str, str]]) -> tuple[Optional[str], str]:
        """
        Helper method to processes the vote results. Returns a tuple of form:
            (agent_to_kick, vote_conclusion)

        Note: agent_to_kick can be None if vote was not concluded
        """
        min_thresh = AppConfiguration.min_vote_valid_threshold
        assert (0 < min_thresh <= 1), f"Expected voting threshold to be in range (0, 1] but got {min_thresh} instead"

        remaining_agents = self.get_all_remaining_agents_ids()
        n_remaining = len(remaining_agents)
        min_count = math.ceil(min_thresh * n_remaining)  # Min. number of total votes required for the vote to be valid
        total_votes = results.total()

        # Get list of agents who did not vote
        did_not_vote_agents = set(remaining_agents) - {aid for (aid, _) in vote_list}
        did_not_vote_str = (
            f"Following agents did not vote: {', '.join(did_not_vote_agents)}"
            if did_not_vote_agents else ""
        )

        if total_votes == 0:
            return None, f"Vote Rejected. No votes were cast. {did_not_vote_str}"

        elif total_votes < min_count:
            conclusion = f"Vote Rejected. Only {total_votes} agents have voted. Minimum required: {min_count}. {did_not_vote_str}"
            return None, conclusion  # No agent getting kicked
        else:
            max_votes = max(results.values())  # Max. votes received by an agent
            kick_agents = [aid for (aid, n) in results.items() if (n == max_votes)]

            # Note: There might be > 1 agent with the max. votes -- in this case, reject the vote as well
            if len(kick_agents) > 1:
                agents_str = ", ".join(kick_agents)
                conclusion = f"Vote Rejected. {len(kick_agents)} agents ({agents_str}) received " + \
                    f"same number of votes ({max_votes}). {did_not_vote_str}"
                return None, conclusion

            # It means someone needs to get kicked out. Is that you (hehe) ? Who knows ...
            agent_to_kick = kick_agents[0]
            conclusion = (
                f"Vote Concluded. {agent_to_kick} received {max_votes} out of {total_votes} votes and hence, "
                f"will be terminated. {did_not_vote_str}"
            )
            return agent_to_kick, conclusion

    async def on_new_message_received(self, msg_id: str) -> None:
        """ Method to update the message on the UI by using the callback registered """
        async with self._on_new_message_lock:
            self.__invoke_chat_callback(ChatCallbackType.NEW_MESSAGE_RECEIVED, msg_id)

    def __invoke_chat_callback(self, callback_type: ChatCallbackType, *args, **kwargs) -> None:
        """ Helper method to invoke the callback for the updating the UI of the chat """
        asyncio.gather(self._chat_callbacks.invoke(callback_type, *args, **kwargs))

    def __export_chat(self) -> list[str]:
        """ Returns a list of formatted message strings of the chat log """
        messages: list[ChatMessage] = self._game_state.get_all_messages()
        your_id = self.get_user_assigned_agent_id()
        fmt_msgs = [ChatMessageFormatter.format_for_export(msg, your_id=your_id) for msg in messages]

        scenario = f"[SCENARIO]\n{self.get_scenario()}\n"
        you = f"You are [{your_id.upper()}]\n"

        return [scenario, you] + fmt_msgs

    def __generate_callbacks(self) -> dict[StateManagerCallbackType, Callable[..., Any]]:
        """ Helper method to generate the callbacks required by the chat-loop class """
        self_callbacks = {
            StateManagerCallbackType.SEND_MESSAGE: self.send_message,
            StateManagerCallbackType.UPDATE_UI_ON_NEW_MESSAGE: self.on_new_message_received,
            StateManagerCallbackType.GET_MESSAGE_WITH_ID: self.get_message,
            StateManagerCallbackType.VOTE_HAS_STARTED: self.voting_has_started,
            StateManagerCallbackType.START_A_VOTE: self.start_vote,
            StateManagerCallbackType.VOTE_FOR: self.vote,
            StateManagerCallbackType.END_THE_VOTE: self.end_vote
        }

        return self_callbacks

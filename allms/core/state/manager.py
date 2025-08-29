import asyncio
import logging
import math
import random
from collections import Counter
from pathlib import Path
from threading import Lock
from typing import Any, Callable, Optional

from allms.config import AppConfiguration, RunTimeConfiguration
from allms.core.agents import Agent, AgentFactory
from allms.core.chat import ChatMessage, ChatMessageHistory, ChatMessageIDGenerator
from allms.core.generate import PersonaGenerator, ScenarioGenerator
from allms.core.log import GameEventLogs
from allms.core.llm.loop import ChatLoop
from .callbacks import CallbackType, StateManagerCallbacks
from .state import GameState


class GameStateManager:
    """ Class for managing the game state """

    def __init__(self, config: RunTimeConfiguration):
        self._config = config
        self._logger = logging.getLogger(self.__class__.__name__)
        self._msg_id_generator = ChatMessageIDGenerator()
        self._valid_genres = self.get_available_genres()
        self._scenario_generator = ScenarioGenerator()
        self._persona_generator = PersonaGenerator()

        self._scenario: str = ""
        self._game_state: Optional[GameState] = None
        self._on_new_message_lock: Lock = Lock()  # To ensure one update at a time
        self._on_new_message_callback: Optional[Callable] = None

        self._vote_started_timestamp: Optional[int] = None
        self._vote_will_end_on_timestamp: Optional[int] = None

        self._self_callbacks = StateManagerCallbacks(self.__generate_callbacks())
        self._chat_loop: Optional[ChatLoop] = None

    async def new(self) -> None:
        """ Creates a new game state """
        AppConfiguration.logger.log("Creating a new game state ...")
        self._game_state = GameState()
        self.update_scenario(self.generate_scenario())
        self.create_agents(self._config.default_agent_count)

        await self._game_state.messages.initialize()

    def start_llms(self) -> None:
        """ Method to start the chatroom """
        if self._config.ui_dev_mode:
            return

        self._chat_loop = ChatLoop(config=self._config,
                                   your_agent_id=self.get_user_assigned_agent_id(),
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
            AppConfiguration.logger.log(f"Trying to stop {llm_for} when there is no chat loop running", level=logging.WARNING)
            return

        if agent_id is None:
            # TODO: Ensure all agents are stopped before resetting everything
            self._chat_loop.stop()
            self._chat_loop = None
        else:
            self._chat_loop.stop_agents(agent_id)

    def load(self, file_path: str | Path) -> None:
        """ Loads the game state from the given path """
        # TODO: Implement the loading logic
        raise NotImplementedError

    def save(self, file_path: str | Path) -> None:
        """ Saves the game state to persistent storage """
        # TODO: Implement the saving logic
        raise NotImplementedError

    def register_on_new_message_callback(self, on_new_message: Callable) -> None:
        """ Register a callback for handling when new message arrives """
        self._on_new_message_callback = on_new_message
        self._self_callbacks.register_callback(CallbackType.UPDATE_UI_ON_NEW_MESSAGE, on_new_message)

    def on_new_message_received(self, msg_id: str) -> None:
        """ Method to update the message on the UI by using the callback registered """
        assert self._on_new_message_callback is not None, f"Callback for updating message to UI is not registered yet"
        with self._on_new_message_lock:
            self._on_new_message_callback(msg_id)

    def get_scenario(self) -> str:
        """ Returns the current scenario """
        return self._scenario

    def create_agents(self, n_agents: int) -> None:
        """ Creates the agents and assigns them to the state """
        genre = self.get_genre()
        AppConfiguration.logger.log(f"Creating {n_agents} agents for given the genre: '{genre}' ...")
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
            AppConfiguration.logger.log(f"Updating genre to '{genre}' ...")
            self._game_state.update_genre(genre)
            self._scenario_generator = ScenarioGenerator(genre)
            self._persona_generator = PersonaGenerator(genre)

    def update_scenario(self, scenario: str) -> None:
        """ Updates the scenario with the given scenario """
        self.__check_game_state_validity()
        self._scenario = scenario
        AppConfiguration.logger.log(f"Updating scenario to '{scenario}' ...")
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
            AppConfiguration.logger.log(f"Informing {started_by} that you have started the vote as them ...")
            pass  # TODO: Inform the agent that it was you (the human) who started the vote on their behalf

        # New voting has been started -- track the timestamp
        # Need this to ensure vote ends after pre-specified amount of time
        curr_ts = AppConfiguration.clock.current_timestamp_in_milliseconds_utc()
        vote_duration_min = AppConfiguration.max_vote_duration_min

        self._vote_started_timestamp = curr_ts
        self._vote_will_end_on_timestamp = AppConfiguration.clock.add_n_minutes(curr_ts, n_minutes=vote_duration_min)
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
        AppConfiguration.logger.log(f"Vote conclusion: {vote_conclusion}")
        if kick_agent_id is not None:
            self.terminate_agent(kick_agent_id)

        # TODO: Inform agents in their chat-logs that voting has ended, who got how many votes, who got kicked out etc.
        # TODO: Update the UI with a message/toast that the vote has concluded

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
            AppConfiguration.logger.log(f"Informing {by_agent} that you have voted for {for_agent} as them ...")
            pass  # TODO: Inform the agent that it was you (the human) who did the vote on their behalf

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
        AppConfiguration.logger.log(f"{agent_id} terminated", level=logging.CRITICAL)

        # Stop the LLM associated with this agent
        if (agent_id != your_id) and (not won):
            self.stop_llms(agent_id)
            # TODO: Remove this agent from LLMResponseModel's allowed agent IDs list as well
            # TODO: Inform the LLMs in their logs that this was not the human

        # You got caught, or you won -- either ways, the game has ended
        else:
            self.stop_llms()
            self.end_game(won)

    def end_game(self, won: bool) -> None:
        """ Method that stops the game """
        # TODO: Show game ended screen on the UI
        self._game_state.end_game(won)

    async def background_worker(self) -> None:
        """ Worker that runs in background checking for voting status, tracking duration etc. """
        clock = AppConfiguration.clock
        logger = AppConfiguration.logger

        logger.log(f"Starting worker in the the background ...")
        start_ts = clock.current_timestamp_in_milliseconds_utc()
        self._game_state.update_start_time(start_ts)

        try:
            while True:
                await asyncio.sleep(1)  # Give control to others
                curr_ts = clock.current_timestamp_in_milliseconds_utc()
                self._game_state.update_duration(curr_ts)

                # TODO: Check the voting status

        except (asyncio.CancelledError, Exception) as e:
            logger.log(f"Received termination signal for background worker", level=logging.CRITICAL)

        duration = self._game_state.get_duration()
        duration, duration_unit = clock.calculate_duration(duration_ms=duration)
        logger.log(f"Stopping background worker")
        logger.log(f"Elapsed chatroom duration: {duration} {duration_unit}")

    def __create_new_message(self,
                             msg: str,
                             sent_by: str,
                             sent_by_you: bool,
                             sent_to: Optional[str] = None,
                             thought_process: str = "",
                             reply_to_id: Optional[str] = None,
                             suspect_id: Optional[str] = None,
                             suspect_confidence: Optional[int] = None,
                             suspect_reason: Optional[str] = None
                             ) -> ChatMessage:
        """ Helper method to create a message and return it """
        msg_id = self._msg_id_generator.next()
        timestamp = AppConfiguration.clock.current_timestamp_in_iso_format()
        chat_msg = ChatMessage(id=msg_id, timestamp=timestamp, msg=msg, sent_by=sent_by, sent_by_you=sent_by_you,
                               sent_to=sent_to, thought_process=thought_process, reply_to_id=reply_to_id,
                               suspect=suspect_id, suspect_reason=suspect_reason, suspect_confidence=suspect_confidence)
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
            conclusion = f"Vote Concluded. {agent_to_kick} will be terminated. {did_not_vote_str}"
            return agent_to_kick, conclusion

    def __generate_callbacks(self) -> dict[CallbackType, Callable[..., Any]]:
        """ Helper method to generate the callbacks required by the chat-loop class """
        self_callbacks = {
            CallbackType.SEND_MESSAGE: self.send_message,
            CallbackType.GET_MESSAGE_WITH_ID: self.get_message,
            CallbackType.VOTE_HAS_STARTED: self.voting_has_started,
            CallbackType.START_A_VOTE: self.start_vote,
            CallbackType.VOTE_FOR: self.vote,
            CallbackType.END_THE_VOTE: self.end_vote
        }

        return self_callbacks

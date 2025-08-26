import logging
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
        self._scenario_generator = ScenarioGenerator()
        self._persona_generator = PersonaGenerator()

        self._scenario: str = ""
        self._game_state: Optional[GameState] = None
        self._on_new_message_lock: Lock = Lock()  # To ensure one update at a time
        self._on_new_message_callback: Optional[Callable] = None

        self._self_callbacks = StateManagerCallbacks(self.__generate_callbacks())
        self._chat_loop: Optional[ChatLoop] = None

    async def new(self) -> None:
        """ Creates a new game state """
        AppConfiguration.logger.log("Creating a new game state ...")
        self._game_state = GameState()
        self.update_scenario(self.generate_scenario())
        self.create_agents(self._config.default_agent_count)

        await self._game_state.messages.initialize()

    def start(self) -> None:
        """ Method to start the chatroom """
        self._chat_loop = ChatLoop(config=self._config,
                                   your_agent_id=self.get_user_assigned_agent_id(),
                                   agents=self.get_all_agents(),
                                   scenario=self.get_scenario(),
                                   callbacks=self._self_callbacks
                                   )
        # TODO: Handle any pre-processing steps, if any, that might need to be done before loop starts
        self._chat_loop.start()

    def pause(self) -> None:
        """ Method to pause the chatroom """
        assert self._chat_loop is not None, f"Trying to pause chat-loop which doesn't exist"
        self._chat_loop.pause()

    def stop(self) -> None:
        """ Method to stop the chatroom """
        if self._chat_loop is not None:
            # TODO: Ensure all agents are stopped before resetting everything
            self._chat_loop.stop()
            self._chat_loop = None

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
        agents = AgentFactory.create(n_agents)
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

    def generate_persona(self, agent_id: str, agent_ids: list[str]) -> str:
        """ Generates a new agent persona and returns it """
        self.__check_game_state_validity()
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

    def voting_has_started(self) -> bool:
        """ Method that returns True if voting has started, False otherwise """
        return self._game_state.voting_has_started()

    def start_vote(self) -> None:
        """ Method to start the voting process """
        self._game_state.start_voting()

    def end_vote(self) -> Counter:
        """ Method to end the voting process """
        return self._game_state.end_voting()

    def vote(self, by_agent: str, for_agent: str) -> None:
        """ Method to participate in the vote """
        self._game_state.vote(by_agent, for_agent)

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

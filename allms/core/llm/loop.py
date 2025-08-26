import asyncio
import random
from collections import deque
from typing import Iterable, Optional

from allms.config import AppConfiguration, RunTimeConfiguration
from allms.core.agents import Agent
from allms.core.state.callbacks import CallbackType, StateManagerCallbacks
from .manager import LLMAgentsManager
from .response import LLMResponseModel


class ChatLoop:
    """ Class for the main chat loop of the LLMs """

    def __init__(self,
                 config: RunTimeConfiguration,
                 your_agent_id: str,
                 agents: dict[str, Agent],
                 scenario: str,
                 callbacks: StateManagerCallbacks,
                 ):
        self._config = config
        self._your_id = your_agent_id
        self._agents = agents
        self._scenario = scenario
        self._callbacks = callbacks

        self._llm_agent_ids = {agent_id for agent_id in self._agents.keys() if (agent_id != self._your_id)}  # All except you
        self._stop_loop: dict[str, bool] = {aid: False for aid in self._llm_agent_ids}
        self._agent_tasks: dict[str, asyncio.Task] = {}
        self._pause_loop: bool = False

        self._vote_start_time: Optional[int] = None
        self._vote_end_time: Optional[int] = None

        # Maintain a rolling chat history per agent -- includes public messages, DMs and notifications
        # Since the number of agents would be typically small (if you configure it to be a value like > 100, either
        # you're crazy or you have a supercomputer powered by god himself idk), it's okay-ish to maintain redundant
        # global messages per agent
        self._llm_chat_history: dict[str, deque[str]] = {agent_id: deque() for agent_id in self._llm_agent_ids}

        # Set the class attributes of the allowed agent-IDs in the response models
        LLMResponseModel.set_allowed_ids(self._agents.keys())
        self._llm_agents_mgr = LLMAgentsManager(config=config, scenario=scenario, agents=self._agents)

    def start(self) -> None:
        """ Start the loop """
        for agent_id in self._llm_agent_ids:
            AppConfiguration.logger.log(f"Starting agent loop for {agent_id} ... ")
            agent = self._agents[agent_id]
            task = asyncio.create_task(self.agent_loop(agent))
            self._agent_tasks[agent_id] = task

    def pause(self) -> None:
        """ Pauses the loop """
        self._pause_loop = True

    def resume(self) -> None:
        """ Resumes the loop """
        self._pause_loop = False

    def stop(self) -> None:
        """ Stops all the agents """
        self.stop_agents(self._llm_agent_ids)

    def stop_agents(self, agent_ids: str | Iterable[str] = None) -> None:
        """ Stops a given agent or a list of agents. If no agent is provided, stops every agent """
        if agent_ids is None:
            agent_ids = self._llm_agent_ids
        if isinstance(agent_ids, str):
            agent_ids = [agent_ids]

        for agent_id in agent_ids:
            assert agent_id in self._llm_agent_ids, f"Trying to stop agent ID: {agent_id} which is not in the list " + \
                f"of all agent IDs: {self._llm_agent_ids}"
            assert agent_id in self._agent_tasks, f"Trying to cancel agent ID: {agent_id} but is not present in the tasks map"
            self._stop_loop[agent_id] = True
            self._agent_tasks[agent_id].cancel()

    async def agent_loop(self, agent: Agent) -> None:
        """ Main loop of the LLM agent """
        agent_id = agent.id
        voting_not_started_prompt = self._llm_agents_mgr.get_input_prompt(agent_id, voting_has_started=False)

        try:
            while not self._stop_loop[agent.id]:

                # Sleep for N random seconds to simulate delays, like in a group-chat and to prevent spamming
                delay = random.randint(1, 4)
                await asyncio.sleep(delay)
                if self._pause_loop:  # If paused, prevent agents from interacting with the model
                    continue

                curr_time_ms = AppConfiguration.clock.current_timestamp_in_milliseconds_utc()
                vote_started, vote_started_by = await self._callbacks.invoke(CallbackType.VOTE_HAS_STARTED)
                if vote_started:
                    voting_started_prompt = self._llm_agents_mgr.get_input_prompt(agent_id, voting_has_started=True, started_by=vote_started_by)

                # Terminate the vote if the max. duration of the vote has passed or everyone has voted
                # TODO: Check if everyone has voted
                if vote_started and (curr_time_ms > self._vote_end_time):
                    vote_started = False
                    AppConfiguration.logger.log(f"Voting has ended due to timeout")
                    # TODO: Gather the vote results and do whatever needs to be done

                AppConfiguration.logger.log(f"Requesting response from agent ({agent_id}) ... ")
                input_prompt = voting_started_prompt if vote_started else voting_not_started_prompt
                model_response: LLMResponseModel = await self._llm_agents_mgr.generate_response(agent_id, input_prompt=input_prompt)

                if model_response is None:
                    continue

                AppConfiguration.logger.log(f"Received valid response from agent ({agent_id}) ... ")

                # Valid response received from the model
                # Send the message and update the game state
                msg: str = model_response.message
                thought_process: str = model_response.intent
                send_to: Optional[str] = model_response.send_to
                suspect: Optional[str] = model_response.suspect
                suspect_reason: Optional[str] = model_response.suspect_reason
                suspect_confidence: Optional[int] = model_response.suspect_confidence
                start_a_vote: bool = model_response.start_a_vote
                voting_for: Optional[str] = model_response.voting_for

                # 1. Send the message
                msg_id = await self._callbacks.invoke(CallbackType.SEND_MESSAGE, msg=msg, sent_by=agent_id, sent_by_you=False,
                                                      sent_to=send_to, thought_process=thought_process, suspect_id=suspect,
                                                      suspect_reason=suspect_reason, suspect_confidence=suspect_confidence)

                # 2. Update the GUI
                await self._callbacks.invoke(CallbackType.UPDATE_UI_ON_NEW_MESSAGE, msg_id=msg_id)

                # 3. Start the vote if the agent requested to start the vote
                # Note: Vote might have started while the model was generating a response. Recheck again
                vote_started = await self._callbacks.invoke(CallbackType.VOTE_HAS_STARTED)
                if start_a_vote and (not vote_started):
                    AppConfiguration.logger.log(f"{agent_id} has requested to start a vote. Initiating the voting process ...")

                    await self._callbacks.invoke(CallbackType.START_A_VOTE, started_by=agent_id)
                    await self._callbacks.invoke(CallbackType.VOTE_FOR, by_agent=agent_id, for_agent=voting_for)
                    # TODO: Display UI on the screen for voting

                    self._vote_start_time = AppConfiguration.clock.current_timestamp_in_milliseconds_utc()
                    self._vote_end_time = AppConfiguration.clock.add_n_minutes(self._vote_start_time,
                                                                               n_minutes=AppConfiguration.max_vote_duration_min)
        except asyncio.CancelledError:
            # TODO: Handle when the task is cancelled
            AppConfiguration.logger.log(f"Agent ({agent_id}) has been stopped")

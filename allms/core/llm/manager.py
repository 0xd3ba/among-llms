import logging

import instructor

from allms.config import AppConfiguration, RunTimeConfiguration
from allms.core.agents import Agent
from allms.core.chat import ChatMessage, ChatMessageFormatter
from allms.core.state.callbacks import StateManagerCallbackType, StateManagerCallbacks
from .factory import client_factory
from .parser import LLMResponseParser
from .prompt import LLMPromptGenerator
from .response import LLMResponseModel
from .roles import LLMRoles


class LLMAgentsManager:
    """ Class for managing the agents """
    def __init__(self, config: RunTimeConfiguration, scenario: str, agents: dict[str, Agent], callbacks: StateManagerCallbacks):
        self._config = config
        self._scenario = scenario
        self._agents = agents
        self._callbacks = callbacks
        self._prompt = LLMPromptGenerator(scenario=self._scenario, agents=self._agents)
        self._client: instructor.Instructor = client_factory(
            model=self._config.ai_model, 
            is_offline=self._config.offline_model,
            api_key=self._config.openrouter_api_key if hasattr(self._config, 'openrouter_api_key') else None
        )

        self._there_is_a_human_prompt = self.__get_presence_of_human_prompt()
        self._bg_prompt = self.__get_background_prompt()
        self._op_prompt = self.__get_output_prompt()

    async def generate_response(self, agent_id: str, input_prompt: str, terminated_agents: set[str]) -> LLMResponseModel | None:
        """ Generates a response by the LLM and returns it """
        tries = 0
        generated_message = ""
        parsed_response = None

        # Note: Need to include the instructions in the history
        human_prompt = await self.__create_message(content=self._there_is_a_human_prompt)
        bg_prompt = await self.__create_message(content=self._bg_prompt)
        op_prompt = await self.__create_message(content=self._op_prompt)
        ip_prompt = await self.__create_message(content=input_prompt)
        term_prompt = await self.__create_message(content=self._prompt.generate_terminated_agents_prompt(terminated_agents))
        history = await self.__prepare_history(agent_id)
        messages = [bg_prompt] + history + [ip_prompt, human_prompt, term_prompt, op_prompt]

        while tries < AppConfiguration.max_model_retries:
            tries += 1
            response = await self._client.chat.completions.create(
                response_model=None,  # We will handle it ourselves
                model=self._config.ai_model,
                messages=messages
            )

            if (not response) or (not response.choices):
                AppConfiguration.logger.log(f"[{tries}] {agent_id} could not generate a response. Retrying ... ", level=logging.CRITICAL)
                continue

            try:
                # TODO: Need to check if the below line will work with non OpenAI models as I'm currently not sure of it
                # TODO: If doesn't work, then need to come up with a generalized method to extract the contents
                generated_message = (response.choices[0]).message.content
                parsed_response = LLMResponseParser.parse(generated_message)
                break

            except (ValueError, Exception) as e:
                AppConfiguration.logger.log(f"[{tries}] {agent_id} generated a malformed response: {generated_message}. " +
                                            f"Exception: {e}. ENSURE YOU ADHERE TO THE EXPECTED OUTPUT SCHEMA", level=logging.CRITICAL)
                # Add in the exception message to the list of messages inorder for the model to generate a better response next time
                exception_msg = await self.__create_message(content=str(e), role=LLMRoles.system)
                messages.append(exception_msg)
                continue

        # Either the model failed to generate a response properly or it successfully generated the message
        if parsed_response is None:
            AppConfiguration.logger.log(f"{agent_id} exceeded max. tries and could not generate a response. Returning None")
        return parsed_response

    def get_input_prompt(self, agent_id: str, voting_has_started: bool, started_by: str = None, voted_for: str = None) -> str:
        return self._prompt.generate_input_prompt(agent_id, voting_has_started, started_by, voted_for)

    def __get_background_prompt(self) -> str:
        return self._prompt.generate_background_prompt()

    def __get_output_prompt(self) -> str:
        return self._prompt.generate_output_prompt()

    def __get_presence_of_human_prompt(self) -> str:
        return self._prompt.generate_presence_of_human_prompt()

    async def __prepare_history(self, agent_id: str) -> list[dict[str, str]]:
        """ Helper method to prepare the message history of the agent required for context """
        agent = self._agents[agent_id]
        chat_log = agent.get_chat_logs()  # Each item is of form (role, message/message_ID, is_message_id)

        # Each message must be of the following format
        # {"role": "user",      "content": <message>} for messages by other agents
        # {"role": "assistant", "content": <message>} for messages by this agent
        messages = []
        for (role, msg, is_id) in chat_log:
            message = await self.__create_message(role=role, content=msg, is_message_id=is_id)
            messages.append(message)

        return messages

    async def __create_message(self, content: str, role: str = LLMRoles.system, is_message_id: bool = False) -> dict[str, str]:
        """ Helper method to create the dict in the format required """
        # If the contents is actually a message ID, need to fetch the message contents and then format it
        if is_message_id:
            msg: ChatMessage = await self._callbacks.invoke(StateManagerCallbackType.GET_MESSAGE_WITH_ID, content)
            content = ChatMessageFormatter.format_to_string(msg)

        message = dict(role=role, content=content)
        return message

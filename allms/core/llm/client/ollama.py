from typing import Type, Any, Callable

import instructor
from openai import AsyncOpenAI

from allms.config import ModelTypes, RunTimeModel
from .base import LLMBaseClient, LLMClientResult


class OllamaBaseLLMClient(LLMBaseClient):
    """ Base class for the offline Ollama LLM client """

    @classmethod
    def create_client(cls, model: RunTimeModel) -> LLMClientResult:
        """ Creates the Ollama client and returns it """
        cls.validate_arguments()
        server_port = model.offline_server_port
        ollama_client = cls.async_client_cls(
            base_url=f"http://localhost:{server_port}/v1",  # Ollama default
            api_key="ollama",                               # dummy key, Ollama ignores it
        )

        client = cls.instructor_callable(ollama_client)
        return LLMClientResult(model=model.name, client=client)


class OllamaOpenAILLMClient(OllamaBaseLLMClient):
    """ Class for Ollama client for OpenAI models """
    async_client_cls: Type[Any] = AsyncOpenAI
    instructor_callable: Type[Callable] = instructor.from_openai

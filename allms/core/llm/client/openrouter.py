import os
from typing import Any, Callable, Type

import instructor
from openai import AsyncOpenAI

from allms.config import ModelTypes, RunTimeModel
from .base import LLMBaseClient, LLMClientResult


class OpenRouterBaseLLMClient(LLMBaseClient):
    """ Base class for online OpenRouter LLM client """

    # Mapping between a model type and the name used by OpenRouter
    # When you support a new model, make sure you add the appropriate name mapping here
    _model_name_map: dict[ModelTypes, str] = {
        ModelTypes.gpt_oss_20b: "openai/gpt-oss-20b:free",
        ModelTypes.gpt_oss_120b: "openai/gpt-oss-120b:free",
    }

    @classmethod
    def create_client(cls, model: RunTimeModel) -> LLMClientResult:
        """ Creates the appropriate OpenRouter client and returns it """
        cls.validate_arguments()
        client = cls.async_client_cls(
            base_url=f"https://openrouter.ai/api/v1",
            api_key=os.getenv(model.env_var_api_key),
        )

        client = cls.instructor_callable(client)

        model_type = ModelTypes(model.name)
        if model_type not in OpenRouterBaseLLMClient._model_name_map:
            raise RuntimeError(f"Did you forget to add name mapping for {model.name} in OpenRouter's model name map ?")
        model_name = OpenRouterBaseLLMClient._model_name_map[model_type]

        return LLMClientResult(model=model_name, client=client)


class OpenRouterOpenAILLMClient(OpenRouterBaseLLMClient):
    """ Class for OpenRouter LLM client for OpenAI models """
    async_client_cls: Type[Any] = AsyncOpenAI
    instructor_callable: Type[Callable] = instructor.from_openai

    # Note: It seems OpenAI's GPT-OSS models are providing invalid responses everytime when used with OpenRouter
    # I don't know why, needs some serious investigation.

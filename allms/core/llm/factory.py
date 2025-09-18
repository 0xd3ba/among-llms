from typing import Type

from allms.config import ModelTypes, ModelProviderTypes, RunTimeModel
from allms.core.llm.client import *


class ClientFactory:
    """ Factory class for the instructor clients """
    def __init__(self):
        # A mapping between the model types and the corresponding class to return an instructor instance
        self._models_map: dict[tuple[ModelTypes, ModelProviderTypes], Type[LLMBaseClient]] = {
            # Offline model mappings
            (ModelTypes.gpt_oss_20b, ModelProviderTypes.ollama): OllamaOpenAILLMClient,
            (ModelTypes.gpt_oss_120b, ModelProviderTypes.ollama): OllamaOpenAILLMClient,

            # Online model mappings
            (ModelTypes.gpt_oss_20b, ModelProviderTypes.openrouter): OpenRouterOpenAILLMClient,
            (ModelTypes.gpt_oss_120b, ModelProviderTypes.openrouter): OpenRouterOpenAILLMClient,

            # Add your model here as a (model_type, provider_type) tuple
            # Note: If your model is not offline, you will need to set its appropriate API key in an environment variable
        }

    def create(self, model: RunTimeModel) -> LLMClientResult:
        """ Instantiates an instructor client and returns it """
        model_type, model_provider = self.__check_if_supported(model)
        client_cls = self._models_map[(model_type, model_provider)]
        return client_cls.create_client(model)

    def __check_if_supported(self, model: RunTimeModel) -> tuple[ModelTypes, ModelProviderTypes]:
        """ Helper method to check if the given model is supported """
        model_type = ModelTypes(model.name)
        model_provider = ModelProviderTypes(model.provider)

        if (model_type, model_provider) not in self._models_map:
            raise RuntimeError(
                f"Provided model_name={model.name}, provider={model.provider}) is not present in the map. "
                f"Either it is not supported or you have forgot to include it in the map"
            )

        return model_type, model_provider

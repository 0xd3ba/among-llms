from typing import Type

from instructor import Instructor

from allms.config import ModelTypes, RunTimeModel
from .client import *


class ClientFactory:
    """ Factory class for the instructor clients """
    def __init__(self):
        # A mapping between the model types and the corresponding class to return an instructor instance
        self._models_map: dict[tuple[ModelTypes, bool], Type[LLMBaseClient]] = {
            (ModelTypes.gpt_oss_20b, True): OllamaOfflineLLMClient,
            (ModelTypes.gpt_oss_120b, True): OllamaOfflineLLMClient,
            # Add your model here as a (model_type, is_offline) tuple
            # Note: If your model is not offline, you will need to set its appropriate API key in an environment variable
        }

    def create(self, model: RunTimeModel) -> Instructor:
        """ Instantiates an instructor client and returns it """
        model_type, model_offline = self.__check_if_supported(model)
        client_cls = self._models_map[(model_type, model_offline)]
        return client_cls.create_client(model)

    def __check_if_supported(self, model: RunTimeModel) -> tuple[ModelTypes, bool]:
        """ Helper method to check if the given model is supported """
        try:
            model_type = ModelTypes(model.name)
            model_offline = model.offline_model
        except ValueError as ve:
            raise ValueError(f"model={model.name} is not present inside ModelTypes")

        if (model_type, model_offline) not in self._models_map:
            raise RuntimeError(
                f"Provided model_name={model.name}, is_offline={model_offline}) is not present in the map. "
                f"Either it is not supported or you have forgot to include it in the map"
            )

        return model_type, model_offline

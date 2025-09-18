from typing import Any, Callable, Type

import instructor

from allms.config import RunTimeModel


class LLMClientResult:
    """ Class for the result of an LLM client """
    def __init__(self, model: str, client: instructor.Instructor):
        self._model = model
        self._client = client

    @property
    def model(self) -> str:
        return self._model

    @property
    def client(self) -> instructor.Instructor:
        return self._client


class LLMBaseClient:
    """ Base Class for the LLM client """

    async_client_cls: Type[Any] = None
    instructor_callable: Type[Callable] = None

    @classmethod
    def create_client(cls, model: RunTimeModel) -> LLMClientResult:
        """ Creates the client and returns it """
        # Note: If you want a different client, inherit from this class and initialize it here
        # However make sure you wrap it with instructor appropriately (as long as it is supported)
        # If your model is an online model, extract the API key via os.getenv(model.env_var_api_key) and pass it
        # to the corresponding client accordingly
        raise NotImplementedError

    @classmethod
    def validate_arguments(cls) -> None:
        """ Method to validate the required arguments """
        if cls.async_client_cls is None:
            raise RuntimeError(f"Async client class for {cls.__name__} is not set")
        if cls.instructor_callable is None:
            raise RuntimeError(f"Async client class for {cls.__name__} is not set")

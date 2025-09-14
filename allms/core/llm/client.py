import instructor
from openai import AsyncOpenAI

from allms.config import RunTimeModel


class LLMBaseClient:
    """ Base Class for the LLM client """

    @staticmethod
    def create_client(model: RunTimeModel) -> instructor.Instructor:
        """ Creates the client and returns it """
        # Note: If you want a different client, inherit from this class and initialize it here
        # However make sure you wrap it with instructor appropriately (as long as it is supported)
        # If your model is an online model, extract the API key via os.getenv(model.env_var_api_key) and pass it
        # to the corresponding client accordingly
        raise NotImplementedError


class OllamaOfflineLLMClient(LLMBaseClient):
    """ Class for the offline Ollama LLM client """

    @staticmethod
    def create_client(model: RunTimeModel) -> instructor.Instructor:
        """ Creates the Ollama client and returns it """
        server_port = model.offline_server_port
        ollama_client = AsyncOpenAI(
            base_url=f"http://localhost:{server_port}/v1",  # Ollama default
            api_key="ollama",                               # dummy key, Ollama ignores it
        )

        client = instructor.from_openai(ollama_client)
        return client

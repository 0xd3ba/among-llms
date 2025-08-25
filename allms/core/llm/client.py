import instructor
from openai import OpenAI


class LLMBaseClient:
    """ Base Class for the LLM client """

    @staticmethod
    def create_client(api_key: str = None) -> instructor.Instructor:
        """ Creates the client and returns it """
        # Note: If you want a different client, inherit from this class and initialize it here
        # However make sure you wrap it with instructor appropriately (as long as it is supported)
        raise NotImplementedError


class OllamaOfflineLLMClient(LLMBaseClient):
    """ Class for the offline Ollama LLM client """

    @staticmethod
    def create_client(api_key: str = None) -> instructor.Instructor:
        """ Creates the Ollama client and returns it """
        ollama_client = OpenAI(
            base_url="http://localhost:11434/v1",  # Ollama default
            api_key="ollama",                      # dummy key, Ollama ignores it
        )

        client = instructor.from_openai(ollama_client)
        return client

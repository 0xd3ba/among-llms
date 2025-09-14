import instructor
from openai import AsyncOpenAI


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
        ollama_client = AsyncOpenAI(
            base_url="http://localhost:11434/v1",  # Ollama default
            api_key="ollama",                      # dummy key, Ollama ignores it
        )

        client = instructor.from_openai(ollama_client)
        return client


class OpenRouterLLMClient(LLMBaseClient):
    """ Class for the OpenRouter LLM client """

    @staticmethod
    def create_client(api_key: str = None) -> instructor.Instructor:
        """ Creates the OpenRouter client and returns it """
        if not api_key:
            raise ValueError("OpenRouter API key is required but not provided")
        
        openrouter_client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            default_headers={
                "HTTP-Referer": "https://github.com/0xd3ba/among-llms",
                "X-Title": "Among LLMs"
            }
        )

        client = instructor.from_openai(openrouter_client)
        return client

## Supporting Other Ollama Models
This project currently supports **OpenAI**’s `gpt-oss:20b` and `gpt-oss:120b` models **locally**.
If you’d like to experiment with online models or other Ollama models, a few configuration steps are required before you can use them with Among LLMs.

1. Go to [`config.py`](../allms/config.py) and add the model(s) names to the following list
    ```python
    # List of AI models supported
    ai_models: list[str] = [
        "gpt-oss:20b",
        "gpt-oss:120b",
        # Add the names of your models here
    ]
    ```
    If you only plan to use Ollama models **locally**, you can **skip directly to step-3**.
   
2. Go to [`client.py`](../allms/core/llm/client.py), create a new class for your model(s) such that it inherits the
`LLMBaseClient` and overrides the following method:
    ```python
    def create_client(api_key: str = None) -> instructor.Instructor:
        # Return an instance of your instructor class
    ```
   Implement the method so that it returns an appropriate **asynchronous** [`instructor`](https://python.useinstructor.com/) 
   instance of your model (you will need an API key if your model is **online**. You can set it via an environment variable 
   or hardcode it (not recommended).). Refer to `instructor`'s documentation for implementation details specific to your model.

3. Go to [`factory.py`](../allms/core/llm/factory.py) and add a mapping entry for your new model inside, such that it maps to the
appropriate client class that you implemented in step-2 (you can simply reuse `OllamaOfflineLLMClient` for local Ollama models):
    ```python
   def client_factory(model: str, is_offline: bool) -> Instructor:
    """ Factory method for the client """
        models_map = {
            ("gpt-oss:20b", True): OllamaOfflineLLMClient,
            ("gpt-oss:120b", True): OllamaOfflineLLMClient,
            # Add your model here as a (model_name, is_offline) tuple
            # Note: If your model is not offline, you will need to set its appropriate API key in an environment variable
        }
    ```
    For example if you wise to use Ollama's `gemma3:4b` **locally**, add the following entry:
   `("gemma3:4b", True): OllamaOfflineLLMClient`

4. Finally, go to [`config.yml`](../config.yml) and set the model parameter to use your model
    ```yaml
    model: gemma3:4b
    ```

If you did everything correctly, the application should *hopefully* work with your model.
> [!NOTE]
> Compatibility is not guaranteed for non-OpenAI models as of now.

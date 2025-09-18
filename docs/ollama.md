## Supporting Other Models
This project currently supports **OpenAI**’s `gpt-oss:20b` and `gpt-oss:120b` models **locally**.
If you’d like to experiment with online models or other Ollama models, a few configuration steps are required before you can use them with Among LLMs.

1. Go to [`config/types.py`](../allms/config/types.py) and add an entry for your model in `ModelTypes` class:
   ```python
   class ModelTypes(str, Enum):
    """ Class containing the supported models """
       gpt_oss_20b: str = "gpt-oss:20b"
       gpt_oss_120b: str = "gpt-oss:120b"
   
       # Add the names of your models here.
    
   ```
   
   Go to [`config/models.py`](../allms/config/models.py), inherit the `BaseModelConfiguration` class to create a derived class for your model. For OpenAI
   models, you do not need to do anything as you can simply use `OpenAIGPTModel` class in step-2, which is already defined.
   For other models, simply refer to `OpenAIGPTModel` as a reference and create a similar class.   
   **Note**: Reasoning level terminologies might be different from OpenAI's.


2. Modify `ModelProviderTypes` in [`config/types.py`](../allms/config/types.py) (only if you wish to support an existing
or new online model by a different provider) by adding a new entry accordingly. For local Ollama models, you don't have to do anything.
   ```python
   class ModelProviderTypes(str, Enum):
    """ Class containing the types for supported model providers """
    ollama: str = "ollama"
    openrouter: str = "openrouter"
   
    # Add the name of your provider here
   ```

3. Go to [`config/app.py`](../allms/config/app.py) and add the model(s) to the following mapping inside `AppConfiguration` class.
    ```python
    # AI models supported
    ai_models: dict[ModelTypes, BaseModelConfiguration] = {
        ModelTypes.gpt_oss_20b: OpenAIGPTModel(model_type=ModelTypes.gpt_oss_20b, offline=True, online=False),
        ModelTypes.gpt_oss_120b: OpenAIGPTModel(model_type=ModelTypes.gpt_oss_120b, offline=True, online=False),
        # Add your model instance here. For OpenAI GPT models, just use OpenAIGPTModel class.
        # If you are adding online support for gpt-oss:20b or gpt-oss:120b, simply set online=True here
    }
    ```
    If you only plan to use Ollama models **locally**, you can **skip directly to step-4**.
   

3. Go to [`llm/client/`](../allms/core/llm/client/), create a new class for your model(s) inside appropriate provider, 
such that it inherits the `LLMBaseClient` or the provider's base client (which in-turn inherits `LLMBaseClient`) and 
overrides the following method:
    ```python
    def create_client(model: RunTimeModel) -> LLMClientResult:
        # Return an instance of your LLMClientResult
        # If your model is an online model, extract the API key via os.getenv(model.env_var_api_key)
        # and pass it to the corresponding client accordingly
    ```
   Implement the method so that it creates an appropriate **asynchronous** [`instructor`](https://python.useinstructor.com/) 
   instance of your model and returns an object of `LLMClientResult`. Refer to `instructor`'s documentation for 
implementation details specific to your model. **As an example, please refer to** [`client/openrouter.py`](../allms/core/llm/client/openrouter.py).


4. Go to [`factory.py`](../allms/core/llm/factory.py) and add a mapping entry for your new model (and provider) inside `ClientFactory`, such that it maps to the
appropriate client class that you implemented in step-3 (you can simply reuse `OllamaOfflineLLMClient` for local Ollama models
and `ModelProviderTypes.ollama` as the provider type):
    ```python
    # A mapping between the model types and the corresponding class to return an instructor instance
        self._models_map: dict[tuple[ModelTypes, ModelProviderTypes], Type[LLMBaseClient]] = {
            # Offline model mappings
            (ModelTypes.gpt_oss_20b, ModelProviderTypes.ollama): OllamaOpenAILLMClient,
            (ModelTypes.gpt_oss_120b, ModelProviderTypes.ollama): OllamaOpenAILLMClient,

            # Online model mappings
            (ModelTypes.gpt_oss_20b, ModelProviderTypes.openrouter): OpenRouterOpenAILLMClient,
            (ModelTypes.gpt_oss_120b, ModelProviderTypes.openrouter): OpenRouterOpenAILLMClient,

            # Add your model here as a (model_type, provider_type) tuple that maps to corresponding class
            # Note: If your model is not offline, you will need to set its appropriate API key in an environment variable
        }
    ```

5. Finally, go to [`config.yml`](../config.yml) and either replace the `use_model` parameter's **first** entry to use your 
model (if you wish to use only a single model) or add a new entry for your model (if you wish to use multiple models
inside chatroom)
    ```yaml
    use_models:
      - name: <Your Model> 
        provider: <Your Model Provider>
        offline_model: <True/False> 
        reasoning_level: <Appropriate Reasoning Level>
        env_var_api_key: <Environment Variable Holding the API Key>        
     ```

If you did everything correctly, the application should *hopefully* work with your model.
> [!NOTE]
> Compatibility is not guaranteed for non-OpenAI models as of now.

> [!IMPORTANT]
> As of now, supporting multiple models inside chatroom is still in experimental phase and may not work as intended.
## Supporting Other Ollama Models
This project currently supports **OpenAI**’s `gpt-oss:20b` and `gpt-oss:120b` models **locally**.
If you’d like to experiment with online models or other Ollama models, a few configuration steps are required before you can use them with Among LLMs.

1. Go to [`config/models.py`](../allms/config/models.py) and add an entry for your model in `ModelTypes` class:
   ```python
   class ModelTypes(str, Enum):
    """ Class containing the supported models """
       gpt_oss_20b: str = "gpt-oss:20b"
       gpt_oss_120b: str = "gpt-oss:120b"
   
       # Add the names of your models here.
    
   ```
   
   In the same file, inherit the `BaseModelConfiguration` class to create a derived class for your model. For OpenAI
   models, you do not need to do anything as you can simply use `OpenAIGPTModel` class in step-2, which is already defined.
   For other models, simply refer to `OpenAIGPTModel` as a reference and create a similar class.   
   **Note**: Reasoning level terminologies might be different from OpenAI's.


2. Go to [`config/app.py`](../allms/config/app.py) and add the model(s) to the following mapping inside `AppConfiguration` class.
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
   

3. Go to [`client.py`](../allms/core/llm/client.py), create a new class for your model(s) such that it inherits the
`LLMBaseClient` and overrides the following method:
    ```python
    def create_client(model: RunTimeModel) -> instructor.Instructor:
        # Return an instance of your instructor class
        # If your model is an online model, extract the API key via os.getenv(model.env_var_api_key)
        # and pass it to the corresponding client accordingly
    ```
   Implement the method so that it returns an appropriate **asynchronous** [`instructor`](https://python.useinstructor.com/) 
   instance of your model (you will need an API key if your model is **online**. You will need to set it via an environment 
   variable. Refer to `instructor`'s documentation for implementation details specific to your model.


4. Go to [`factory.py`](../allms/core/llm/factory.py) and add a mapping entry for your new model inside `ClientFactory`, such that it maps to the
appropriate client class that you implemented in step-3 (you can simply reuse `OllamaOfflineLLMClient` for local Ollama models):
    ```python
    self._models_map: dict[tuple[ModelTypes, bool], Type[LLMBaseClient]] = {
         (ModelTypes.gpt_oss_20b, True): OllamaOfflineLLMClient,
         (ModelTypes.gpt_oss_120b, True): OllamaOfflineLLMClient,
         # Add your model here as a (model_type, is_offline) tuple.
    }
    ```

5. Finally, go to [`config.yml`](../config.yml) and either replace the `use_model` parameter's **first** entry to use your 
model (if you wish to use only a single model) or add a new entry for your model (if you wish to use multiple models
inside chatroom)
    ```yaml
    use_models:
      - name: <Your Model> 
        offline_model: <True/False> 
        reasoning_level: <Appropriate Reasoning Level>
        env_var_api_key: <Environment Variable Holding the API Key>        
     ```

If you did everything correctly, the application should *hopefully* work with your model.
> [!NOTE]
> Compatibility is not guaranteed for non-OpenAI models as of now.

> [!IMPORTANT]
> As of now, supporting multiple models inside chatroom is still in experimental phase and may not work as intended.
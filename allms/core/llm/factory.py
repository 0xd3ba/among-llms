from instructor import Instructor

from .client import *


def client_factory(model: str, is_offline: bool, api_key: str = None) -> Instructor:
    """ Factory method for the client """
    models_map = {
        ("gpt-oss:20b", True): OllamaOfflineLLMClient,
        ("gpt-oss:120b", True): OllamaOfflineLLMClient,
        ("deepseek/deepseek-chat-v3.1:free", False): OpenRouterLLMClient,
        # Add your model here as a (model_name, is_offline) tuple
        # Note: If your model is not offline, you will need to set its appropriate API key
    }

    supported_configs = "\n".join([f"model={model}: offline={is_offline}" for (model, is_offline) in models_map.items()])
    assert tuple([model, is_offline]) in models_map, f"Given configuration: ({model}, {is_offline}) is not supported" + \
        f"Supported model configurations: {supported_configs}"

    model_cls = models_map[(model, is_offline)]
    
    # Pass API key to the client if it's an online model
    if not is_offline and api_key:
        return model_cls.create_client(api_key=api_key)
    else:
        return model_cls.create_client()

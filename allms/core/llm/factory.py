from instructor import Instructor

from .client import *


def client_factory(model: str, is_offline: bool) -> Instructor:
    """ Factory method for the client """
    models_map = {
        ("gpt-oss-20b", True): OllamaOfflineLLMClient,
        ("gpt-oss:120b", True): OllamaOfflineLLMClient,
        # Add your model here as a (model_name, is_offline) tuple
        # Note: If your model is not offline, you will need to set its appropriate API key in an environment variable
    }

    # TODO: Extract the API key and pass it to create_client if the model is not offline

    supported_configs = "\n".join([f"model={model}: offline={is_offline}" for (model, is_offline) in models_map.items()])
    assert tuple([model, is_offline]) in models_map, f"Given configuration: ({model}, {is_offline}) is not supported" + \
        f"Supported model configurations: {supported_configs}"

    model_cls = models_map[(model, is_offline)]
    return model_cls.create_client()

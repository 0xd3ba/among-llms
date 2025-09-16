class OllamaConfiguration:
    """ Class for storing Ollama configuration """
    # Note: Do not add any custom configuration that is only specific to your needs
    # This is only meant for storing those constants that is the same for everyone using ollama

    default_local_port: int = 11434  # The default server port used by Ollama models when hosted locally

from __future__ import annotations
from enum import Enum


class ThemeTypes(str, Enum):
    """ Class containing the types for the supported custom app themes """
    # Built-in textual themes
    textual_dark: str = "textual-dark"
    textual_light: str = "textual-light"
    nord: str = "nord"
    gruvbox: str = "gruvbox"
    catppuccin_mocha: str = "catppuccin-mocha"
    dracula: str = "dracula"
    tokyo_night: str = "tokyo-night"
    monokai: str = "monokai"
    flexoki: str = "flexoki"
    catppuccin_latte: str = "catppuccin-latte"
    solarized_light: str = "solarized-light"

    # Custom themes from here on
    # Light themes
    # TODO: Add custom light themes

    # Dark themes
    ms_dos: str = "ms-dos"


class ModelProviderTypes(str, Enum):
    """ Class containing the types for supported model providers """
    ollama: str = "ollama"
    openrouter: str = "openrouter"

    @classmethod
    def is_offline_provider(cls, provider: ModelProviderTypes) -> bool:
        """ Returns True if the model provider is offline """
        return provider == ModelProviderTypes.ollama

    @classmethod
    def is_online_provider(cls, provider: ModelProviderTypes) -> bool:
        """ Returns True if the model provider is online """
        return not cls.is_offline_provider(provider)


class ModelTypes(str, Enum):
    """ Class containing the types for supported models """
    gpt_oss_20b: str = "gpt-oss:20b"
    gpt_oss_120b: str = "gpt-oss:120b"

    # Add the names of your models here


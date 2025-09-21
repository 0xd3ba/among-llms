from __future__ import annotations
from dataclasses import asdict
from typing import Type

from allms.config import ThemeTypes
from .themes import *

from textual.theme import Theme, BUILTIN_THEMES


class CustomThemeFactory:
    """ Class for managing the custom themes """
    # Mapping between a theme type and its corresponding custom theme class
    # When you define a new custom theme, make sure you include its class in this mapping
    _theme_map: dict[ThemeTypes, Type[CustomTheme]] = {
        ThemeTypes.ms_dos: MSDOSTheme,
    }

    @classmethod
    def get_theme(cls, theme_type: ThemeTypes) -> Theme:
        """ Returns the theme specified """
        # Check if the theme is a built-in theme
        if theme_type.value in BUILTIN_THEMES:
            return BUILTIN_THEMES[theme_type.value]

        if theme_type not in cls._theme_map:
            raise RuntimeError(f"Requesting '{theme_type.value}' theme but it has not been registered yet")

        theme_cls = cls._theme_map[theme_type]
        theme_params = asdict(theme_cls())
        theme = Theme(**theme_params)
        return theme

    @classmethod
    def get_all_themes(cls) -> list[Theme]:
        return [cls.get_theme(theme_type) for theme_type in cls._theme_map]

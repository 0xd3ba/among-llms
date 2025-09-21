import re
from dataclasses import field, asdict
from pydantic import field_validator
from pydantic.dataclasses import dataclass

from allms.config import ThemeTypes

from textual.theme import Theme


@dataclass(frozen=True)
class CustomTheme:
    """ Class for a theme """
    # Refer to the following guide for more details
    # https://textual.textualize.io/guide/design/
    name: str        # Name of the theme
    primary: str     # Primary color, can be considered the branding color
    secondary: str   # Secondary color - An alternative branding color
    accent: str      # Used sparingly to draw attention. Typically contrasts with primary and secondary color
    foreground: str  # Default text color
    background: str  # Default background color for screens
    surface: str     # Default background color of widgets, typically sitting on top of background.
    success: str     # Used to indicate success. Typically used as a background color
    warning: str     # Used to indicate a warning. Typically used as a background color
    error: str       # Used to indicate an error. Typically used as a background color
    dark: bool       # Is the theme a dark theme ?

    @field_validator("primary", "secondary", "accent", "foreground", "background", "surface", "success", "warning", "error")
    def _validate_color(cls, v: str) -> str:
        """ Validates the given hex color """
        if not v:
            raise ValueError(f"Color value cannot be an empty string")
        hex_regex = r"^#[0-9a-fA-F]{6}$"  # Regex to match hexadecimal color strings of form: #RRGGBB
        if not re.fullmatch(hex_regex, v):
            raise ValueError(f"Invalid color '{v}'. Expected a hex color in #RRGGBB format")
        return v

    def __post_init__(self):
        CustomThemeManager.register_theme(ThemeTypes(self.name), self)


@dataclass(frozen=True)
class CustomThemeManager:
    """ Class for managing the custom themes """
    # Mapping between a theme type and its corresponding theme object
    # Use the register_theme class method to register a theme
    _theme_map: dict[ThemeTypes, CustomTheme] = field(default_factory=dict)

    @classmethod
    def register_theme(cls, theme_type: ThemeTypes, theme: CustomTheme) -> None:
        """ Registers the given theme """
        cls._theme_map[theme_type] = theme

    @classmethod
    def get_theme(cls, theme_type: ThemeTypes) -> Theme:
        """ Returns the theme specified """
        if theme_type not in cls._theme_map:
            raise RuntimeError(f"Requesting '{theme_type.value}' theme but it has not been registered yet")
        theme_obj = cls._theme_map[theme_type]
        theme_params = asdict(theme_obj)
        theme = Theme(**theme_params)
        return theme


# Define your own custom themes from here onwards
# Name convention: <name>Theme. For e.g., MSDOSTheme
# Make sure it inherits CustomTheme

class MSDOSTheme(CustomTheme):
    def __init__(self):
        super().__init__(
            name=ThemeTypes.ms_dos.name,
            primary="#00a8a8",     # Cyan
            secondary="#a8a8a8",   # Gray (same as surface)
            accent="#00a8a8",      # Cyan (same as primary)
            foreground="#0000a8",  # Darkish Blue
            background="#000000",  # Black
            surface="#a8a8a8",     # Gray
            success="#00a8a8",     # Cyan (same as primary)
            warning="#a80000",     # Red (same as error)
            error="#a80000",       # Red
            dark=True
        )

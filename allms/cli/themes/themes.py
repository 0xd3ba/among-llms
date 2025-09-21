from __future__ import annotations
import re
from dataclasses import field
from pydantic import field_validator
from pydantic.dataclasses import dataclass

from allms.config import ThemeTypes


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

    # Optional additional variables used by textual
    # IMPORTANT: Be careful while defining the colors as the checks are not applied here due to multiple possible formats of values
    # Format: {textual_variable: color_value}
    # Refer to the guide (link above) for more details on the exact textual variables etc.
    variables: dict[str, str] = field(default_factory=dict)

    @field_validator("primary", "secondary", "accent", "foreground", "background", "surface", "success", "warning", "error")
    def _validate_color(cls, v: str) -> str:
        """ Validates the given hex color """
        if not v:
            raise ValueError(f"Color value cannot be an empty string")
        hex_regex = r"^#[0-9a-fA-F]{6}$"  # Regex to match hexadecimal color strings of form: #RRGGBB
        if not re.fullmatch(hex_regex, v):
            raise ValueError(f"Invalid color '{v}'. Expected a hex color in #RRGGBB format")
        return v


# Define your own custom themes from here onwards
# Name convention: <name>Theme. For e.g., MSDOSTheme
# Make sure it inherits CustomTheme

class MSDOSTheme(CustomTheme):
    """ Classic old-school MS-DOS inspired theme """
    # TODO: Need to fix the colors as they are pretty horrible
    def __init__(self):
        super().__init__(
            name=ThemeTypes.ms_dos.value,
            primary="#00a8a8",     # Cyan
            secondary="#a8a8a8",   # Gray (same as surface)
            accent="#00a8a8",      # Cyan (same as primary)
            foreground="#a8a8a8",  # Darkish Blue
            background="#0000a8",  # Black
            surface="#a8a8a8",     # Gray
            success="#00a8a8",     # Cyan (same as primary)
            warning="#a80000",     # Red (same as error)
            error="#a80000",       # Red
            dark=True
        )

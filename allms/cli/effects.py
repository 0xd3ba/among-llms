import random
from typing import Any

from textualeffects.effects import EffectType


class TextualEffects:
    """ Class for textual effects """

    type_beams: EffectType = "Beams"
    type_binary_path: EffectType = "BinaryPath"
    type_decrypt: EffectType = "Decrypt"
    type_matrix: EffectType = "Matrix"
    type_print: EffectType = "Print"
    type_rain: EffectType = "Rain"
    type_spotlights: EffectType = "Spotlights"
    type_swarm: EffectType = "Swarm"
    type_unstable: EffectType = "Unstable"
    type_vhs: EffectType = "VHSTape"

    # Mapping between effects and corresponding configuration
    # Set it pre-configured
    __effect_config_map: dict[EffectType, dict[str, Any]] = {
        type_beams:       dict(beam_delay=2, final_wipe_speed=5),
        type_binary_path: dict(movement_speed=5),
        type_decrypt:     dict(typing_speed=5),
        type_matrix:      dict(rain_symbols=["0", "1"], rain_time=3),
        type_print:       dict(print_speed=5),
        type_rain:        dict(movement_speed=5),
        type_spotlights:  dict(search_duration=3, spotlight_count=3),
        type_swarm:       dict(),
        type_unstable:    dict(explosion_speed=5, reassembly_speed=5),
        type_vhs:         dict(total_glitch_time=3),
    }

    @staticmethod
    def get_random_effect() -> tuple[EffectType, dict[str, Any]]:
        """ Returns a random effect as (effect_type, effect_config) """
        random_effect: EffectType = random.choice(list(TextualEffects.__effect_config_map.keys()))
        return random_effect, TextualEffects.__effect_config_map[random_effect]

    @staticmethod
    def get_effect_config(effect: EffectType) -> dict[str, Any]:
        """ Returns the configuration for the specified effect """
        TextualEffects.__effect_exists_check(effect)
        return TextualEffects.__effect_config_map[effect]

    @staticmethod
    def __effect_exists_check(effect: str | EffectType) -> None:
        """ Helper method to check for validity of effect """
        if effect in TextualEffects.__effect_config_map:
            return

        raise ValueError(f"Textual effect {effect} does not exist")

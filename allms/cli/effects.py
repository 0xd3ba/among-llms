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
    type_unstable: EffectType = "Unstable"
    type_vhs: EffectType = "VHSTape"

    # Mapping between effects and corresponding configuration
    # Set it pre-configured
    __effect_config_map: dict[EffectType, dict[str, Any]] = {
        type_beams:       dict(beam_delay=5, final_wipe_speed=1),
        type_binary_path: dict(movement_speed=3),
        type_decrypt:     dict(typing_speed=20),
        type_matrix:      dict(rain_symbols=["0", "1"], rain_time=1),
        type_print:       dict(print_speed=5),
        type_rain:        dict(movement_speed=[0.1, 0.2]),
        type_spotlights:  dict(search_duration=400, spotlight_count=2),
        type_unstable:    dict(explosion_speed=0.5, reassembly_speed=0.5),
        type_vhs:         dict(total_glitch_time=500),
    }

    @staticmethod
    def get_random_effect() -> tuple[EffectType, dict[str, Any]]:
        """ Returns a random effect as (effect_type, effect_config) """
        random_effect: EffectType = random.choice(list(TextualEffects.__effect_config_map.keys()))
        effect_config = TextualEffects.__effect_config_map[random_effect]

        # Set some parameters statically to ensure a slightly longer animation
        effect_config["final_gradient_frames"] = 10
        effect_config["final_gradient_steps"] = (20, )

        return random_effect, effect_config

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

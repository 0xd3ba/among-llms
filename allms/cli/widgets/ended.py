import random

from textual.app import ComposeResult
from textual.binding import BindingType
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import Static

from allms.config import BindingConfiguration, RunTimeConfiguration
from allms.core.state import GameStateManager
from .modal import ModalScreenWidget


class GameEndedWidget(ModalScreenWidget):

    def __init__(self, title: str, config: RunTimeConfiguration, state_manager: GameStateManager, *args, **kwargs):
        super().__init__(title, config, state_manager, *args, **kwargs)
        self._agent_id = self._state_manager.get_user_assigned_agent_id()
        self._won = self._state_manager.get_game_won()
        self._win_msgs = [
            "You beat the bots! Somewhere, an AI just rage-deleted its training data.",
            "Victory! The bots are filing a bug report against you.",
            "Congratulations! You broke the bots’ little digital hearts.",
            "You win! Somewhere, a bot just updated its resume to 'Defeated by Human'.",
            "You’ve outsmarted the machines. Enjoy your fleeting supremacy.",
            "You win! An AI is somewhere rewriting its algorithms in shame.",
            "Humans 1, AI 0. The bots are accepting digital therapy appointments now.",
            "Outsmarted the LLMs with pure human chaos. Respect.",
            "Congratulations! The bots are requesting a version update.",
            "You win! The LLMs did not see that coming.",
            "Winner Winner, LLM Dinner",
            "Flawless! The bots are currently arguing in binary about what went wrong.",
            "Achievement unlocked: Confused an algorithm with basic humanity."
        ]

        self._lost_msgs = [
            "Caught in 4K by the LLMs.",
            "404: Victory not found.",
            "You’ve been Ctrl + Alt + Defeated.",
            "Captured! The LLMs are adding you to their dataset.",
            "The bots pinged ... and ponged you out.",
            "Your stealth attempt has been deprecated.",
            "Bot > Human. End of script.",
            "Busted by LLMs. Welcome to the training set, friend.",
            "The bots caught you ... and now they’re teaching each other how.",
            "Game over. Your strategy has been uploaded to the AI’s to-do list.",
            "You’ve been classified as: Not Very Sneaky™.",
            "Caught! The bots are already composing a victory tweet.",
            "The AI saw through your stealth like an open-source license.",
            "Detected, rejected, and promptly ejected.",
            "Oops! The bots flagged you as 'spam' and hit delete.",
            "You lose. Somewhere, a chatbot just added your failure to its jokes.",
            "Stealth Level: Potato",
        ]

    def compose(self) -> ComposeResult:
        choices_list = self._win_msgs if self._won else self._lost_msgs
        end_text = random.choice(choices_list)
        end_widget = Static(end_text)

        with VerticalScroll():
            yield self._wrap_inside_container(end_widget, Horizontal, cid="game-ended-container")

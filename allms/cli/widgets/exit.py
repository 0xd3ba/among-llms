import asyncio
import random

from textual import on
from textual.app import ComposeResult
from textual.binding import BindingType
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import Button, Label, Static

from allms.cli.callbacks import ChatCallbackType, ChatCallbacks
from allms.config import BindingConfiguration, RunTimeConfiguration
from allms.core.state import GameStateManager
from .modal import ModalScreenWidget


class ChatExitWidget(ModalScreenWidget):

    def __init__(self, title: str, config: RunTimeConfiguration, state_manager: GameStateManager, callbacks: ChatCallbacks, *args, **kwargs):
        super().__init__(title, config, state_manager, *args, **kwargs)
        self._callbacks = callbacks
        self._id_btn_save_and_exit = "exit-btn-export-and-save"
        self._id_btn_exit_no_save = "exit-btn-direct-exit"
        self._exit_msgs = [
            "Time to byte the dust? Save or exit without a trace?",
            "Ctrl + Alt + Escape? Save your stealth or ghost the bots?",
            "Abort mission or save your data? Don’t let the bots RAM your progress!",
            "Logging out ... don’t let the AI catch your cache!",
            "You’re about to commit ... to exiting. Save first?",
            "Press save before the bots debug your disappearance!",
            "Exit without saving? Hope the bots don’t catch your residuals!",
            "Ghost the bots or save your moves? The choice is yours!",
            "Save & vanish or let the AI process your mistakes?",
            "You’re about to logout ... don’t let the bots CTRL your fate!",
            "Quick! Save before the AI does a hard reset on your progress!",
            "Exit without saving? The bots will have a field day!",
            "Save or vanish… choose wisely, agent human!",
            "Don’t let the AI byte your unsaved progress!",
            "Save & escape or leave it for the bots to parse?"
        ]

    def compose(self) -> ComposeResult:
        end_text = random.choice(self._exit_msgs)
        end_widget = Static(end_text)
        confirm_btn, cancel_btn = self._create_confirm_cancel_buttons(
            confirm_btn_id=self._id_btn_save_and_exit,
            cancel_btn_id=self._id_btn_exit_no_save,
            confirm_btn_text="Save and Exit",
            cancel_btn_text="Exit without Saving"
        )

        with VerticalScroll():
            yield self._wrap_inside_container(end_widget, Horizontal, cid="exit-chat-container")
        yield self._wrap_inside_container([cancel_btn, Label(" "), confirm_btn], Horizontal, cid="exit-chat-buttons-container")

        confirm_btn.focus()

    @on(Button.Pressed)
    def button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        if btn_id == self._id_btn_exit_no_save:
            pass  # Nothing
        elif btn_id == self._id_btn_save_and_exit:
            pass  # TODO: Launch the export screen
        else:
            # Should not come to this branch or else there is a bug
            raise RuntimeError(f"What button with id={btn_id} did you click in the exit screen")

        # In either case, we need to pop the screen, then invoke the callback
        self.app.pop_screen()
        asyncio.gather(self._callbacks.invoke(ChatCallbackType.CLOSE_CHATROOM))

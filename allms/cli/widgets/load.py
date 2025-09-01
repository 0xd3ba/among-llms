from pathlib import Path
from typing import Callable

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import Button, Label, Input, DirectoryTree

from allms.config import AppConfiguration, RunTimeConfiguration
from allms.core.state import GameStateManager
from .modal import ModalScreenWidget


class LoadGameStateWidget(ModalScreenWidget):
    """ Class for loading a game state """

    def __init__(self,
                 title: str,
                 config: RunTimeConfiguration,
                 state_manager: GameStateManager,
                 *args, on_confirm_callback: Callable, **kwargs):
        super().__init__(title, config, state_manager, *args, **kwargs)
        self._path = Path(config.save_directory)
        self._on_confirm_callback = on_confirm_callback
        self._input = Input(disabled=True)
        self._dir_explorer = DirectoryTree(path=self._path)

        self._id_btn_load = "load-game-state-btn"
        self._id_btn_cancel = "cancel-game-state-load-btn"

    def compose(self) -> ComposeResult:
        input_title = "Game-State Path"
        with VerticalScroll():
            yield self._wrap_inside_container(self._input, Horizontal, border_title=input_title, cid="load-input-container")
            yield self._wrap_inside_container(self._dir_explorer, Horizontal, use_border=True, cid="load-directory-tree")

        confirm_btn, cancel_btn = self._create_confirm_cancel_buttons(
            confirm_btn_id=self._id_btn_load,
            cancel_btn_id=self._id_btn_cancel,
            confirm_btn_text="Load"
        )

        yield self._wrap_inside_container([cancel_btn, Label(" "), confirm_btn], Horizontal, cid="load-buttons-container")
        self._dir_explorer.focus()

    def watch_path(self, path: str | None) -> None:
        """ Called everytime path is changed """
        self._input.value = path  # TODO: Input not updating as expected

    @on(DirectoryTree.FileSelected)
    def file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """ Event handler when a file is selected """
        self._input.value = str(event.path)  # TODO: Input not updating as expected

    @on(Button.Pressed)
    def button_pressed(self, event: Button.Pressed) -> None:
        """ Event handler when button is pressed """
        btn_id = event.button.id
        if btn_id == self._id_btn_cancel:
            pass

        elif btn_id in [self._id_btn_save, self._id_btn_load]:
            self._on_confirm_callback()

        else:
            raise RuntimeError(f"Invalid button press with id={btn_id} detected on save/load game-state screen")

        # Either case -- need to pop the screen once a button has been pressed
        self.app.pop_screen()

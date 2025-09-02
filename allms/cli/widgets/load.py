from pathlib import Path
from typing import Callable, Iterable

from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import Button, Label, DirectoryTree, Static

from allms.config import AppConfiguration, RunTimeConfiguration
from allms.core.state import GameStateManager
from .modal import ModalScreenWidget


class _JSONDirectoryTree(DirectoryTree):
    """ Directory tree to only show JSON files """
    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        return [path for path in paths if path.is_dir() or path.suffix == ".json"]


class LoadGameStateWidget(ModalScreenWidget):
    """ Class for loading a game state """

    def __init__(self,
                 title: str,
                 config: RunTimeConfiguration,
                 state_manager: GameStateManager,
                 *args, on_confirm_callback: Callable, **kwargs):
        super().__init__(title, config, state_manager, *args, **kwargs)
        self._path = Path(config.save_directory).resolve()
        self._on_confirm_callback = on_confirm_callback
        self._path_widget = Static()
        self._dir_explorer = _JSONDirectoryTree(path=self._path)

        self._id_btn_load = "load-game-state-btn"
        self._id_btn_cancel = "cancel-game-state-load-btn"

    def on_show(self) -> None:
        # Need to do an update after window is displayed to get the proper width of the container
        # in order to ensure proper render of the Static widget without overflowing
        self._path_widget.update(self.__create_rich_text_path(self._path))

    def compose(self) -> ComposeResult:
        input_title = "Save File"
        with VerticalScroll():
            yield self._wrap_inside_container(self._path_widget, Horizontal, border_title=input_title, cid="load-path-container")
            yield self._wrap_inside_container(self._dir_explorer, Horizontal, border_title="Explorer", cid="load-directory-tree")

        confirm_btn, cancel_btn = self._create_confirm_cancel_buttons(
            confirm_btn_id=self._id_btn_load,
            cancel_btn_id=self._id_btn_cancel,
            confirm_btn_text="Load"
        )

        yield self._wrap_inside_container([cancel_btn, Label(" "), confirm_btn], Horizontal, cid="load-buttons-container")
        self._dir_explorer.focus()

    @on(DirectoryTree.FileSelected)
    @on(DirectoryTree.DirectorySelected)
    @on(DirectoryTree.NodeHighlighted)
    def file_selected(self, event: DirectoryTree.FileSelected | DirectoryTree.DirectorySelected | DirectoryTree.NodeHighlighted) -> None:
        """ Event handler when a file/directory is selected/highlighted """
        if isinstance(event, DirectoryTree.NodeHighlighted):
            path = event.node.data.path
        else:
            path = event.path

        # Highlight the path and scroll to the end
        self._path = path
        self._path_widget.update(self.__create_rich_text_path(self._path))

    @on(Button.Pressed)
    def button_pressed(self, event: Button.Pressed) -> None:
        """ Event handler when button is pressed """
        btn_id = event.button.id
        if btn_id == self._id_btn_cancel:
            self.app.pop_screen()

        elif btn_id in [self._id_btn_load, self._id_btn_load]:
            self.app.pop_screen()
            self._on_confirm_callback()

        else:
            raise RuntimeError(f"Invalid button press with id={btn_id} detected on save/load game-state screen")

    def __create_rich_text_path(self, path: Path) -> Text:
        """ Helper method to create a rich renderable for the given path """
        max_width = self.size.width
        padding = 12
        value = "..." + str(path)[-max_width + padding:]
        parent_str = value.replace(path.name, "")

        text = Text()
        text.append(parent_str, style="dim")
        text.append(path.name, style="bold")

        return text

from typing import Type

from textual.containers import Vertical, Container, Horizontal
from textual.widget import Widget
from textual.widgets import Button

from allms.config import RunTimeConfiguration, StyleConfiguration
from allms.core.state import GameStateManager


class ModalScreenWidget(Vertical):
    """ Base class for a modal screen widget """

    def __init__(self, title: str, config: RunTimeConfiguration, state_manager: GameStateManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._title = title
        self._config = config
        self._state_manager = state_manager

        self.border_title = self._title

    def on_mount(self) -> None:
        self.add_class(StyleConfiguration.class_border)
        self.add_class(StyleConfiguration.class_modal_container)

    @staticmethod
    def _create_confirm_cancel_buttons(confirm_btn_id: str,
                                       cancel_btn_id: str,
                                       confirm_btn_text: str = "Confirm",
                                       cancel_btn_text: str = "Cancel"
                                       ) -> tuple[Button, Button]:
        """ Helper method to create confirm and cancel buttons """
        confirm_btn = Button(confirm_btn_text, variant="success", id=confirm_btn_id, compact=True)
        cancel_btn = Button(cancel_btn_text, variant="error", id=cancel_btn_id, compact=True)

        # Set the width to be the same
        max_len = max(len(t) for t in [confirm_btn_text, cancel_btn_text])
        padding = 4
        confirm_btn.styles.width = max_len + padding
        cancel_btn.styles.width = max_len + padding

        return confirm_btn, cancel_btn

    @staticmethod
    def _wrap_inside_container(widgets: Widget | list[Widget],
                               container_cls: Type[Container | Horizontal | Vertical],
                               use_border: bool = False,
                               border_title: str = "",
                               cid: str = "",
                               ) -> Container:
        """ Helper method to wrap a given widget inside a container and style it """
        if not isinstance(widgets, list):
            widgets = [widgets]

        container = container_cls(*widgets)
        container.border_title = border_title
        container.add_class("new-chatroom-container")

        if cid:
            container.id = cid

        if border_title or use_border:
            container.add_class(StyleConfiguration.class_border)
            container.add_class(StyleConfiguration.class_border_highlight)

        return container

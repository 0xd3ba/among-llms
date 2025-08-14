from typing import Type

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widget import Widget
from textual.widgets import Label, TextArea, Select, Button

from allms.config import AppConfiguration, RunTimeConfiguration, StyleConfiguration


# TODO: Add support for randomizing scenario, agent personas and screen for customizing agent personas
class NewChatroomWidget(Vertical):
    def __init__(self, title, config: RunTimeConfiguration, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._config = config
        self.border_title = title

        min_agents = AppConfiguration.min_agent_count
        max_agents = self._config.max_agent_count
        # Choices should be of following type: (value_displayed_in_UI, value_returned_on_selection)
        self._n_agents_choices = [(str(i), i) for i in range(min_agents, max_agents + 1)]
        self._default_n_agents = (min_agents + max_agents) // 2

        self._id_btn_confirm = "new-chat-confirm"
        self._id_btn_cancel = "new-chat-cancel"

    def on_mount(self) -> None:
        self.add_class(StyleConfiguration.class_border)
        self.add_class(StyleConfiguration.class_modal_container)

    def compose(self) -> ComposeResult:
        scenario_textbox = TextArea(show_line_numbers=True)
        num_agents_list = Select(options=self._n_agents_choices, allow_blank=False, value=self._default_n_agents, compact=True)
        confirm_btn = Button("Confirm", variant="success", id=self._id_btn_confirm)
        cancel_btn = Button("Cancel", variant="error", id=self._id_btn_cancel)

        scenario_textbox.focus()
        with VerticalScroll() as v:
            yield self.__wrap_inside_container(scenario_textbox, Horizontal, border_title="Scenario", cid="scenario-textbox")
            yield self.__wrap_inside_container(num_agents_list, Horizontal, border_title="No. of Agents")

        yield Label()
        yield self.__wrap_inside_container([cancel_btn, Label(" "), confirm_btn], Horizontal, cid="new-chat-buttons")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """ Event handler for button clicked event """
        btn_pressed_id = event.button.id
        if btn_pressed_id == self._id_btn_cancel:
            self.app.pop_screen()
        elif btn_pressed_id == self._id_btn_confirm:
            self.app.pop_screen()
            # TODO: Launch a new screen and start the chat
        else:
            # Should not arrive at this branch or else there is a bug
            raise RuntimeError(f"Received a button pressed event from button-id({btn_pressed_id}) on {self.__class__.__name__}")

    @staticmethod
    def __wrap_inside_container(widgets: Widget | list[Widget],
                                container_cls: Type[Container | Horizontal | Vertical],
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

        if border_title:
            container.add_class(StyleConfiguration.class_border)
            container.add_class(StyleConfiguration.class_border_highlight)

        return container

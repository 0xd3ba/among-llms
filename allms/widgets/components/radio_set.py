from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import RadioButton, RadioSet

from allms.config import StyleConfiguration


class RadioSetComponent(Vertical):
    """ A generic class for set of radio buttons """

    def __init__(self, choices: list[str], title: str = "", default_choice: int = 0):
        super().__init__()
        self._default_choice = default_choice
        self.border_title = title
        self._radio_buttons = [RadioButton(c) for c in choices]

        assert len(choices) > 0, f"For title={title}, the number of choices provided is 0"
        assert 0 <= default_choice < len(choices), f"Provided default choice({default_choice}) should be < # of choices ({len(choices)})"

    def on_mount(self) -> None:
        self.add_class(StyleConfiguration.css_class_round_border)
        self.add_class(StyleConfiguration.css_class_highlight_border_on_focus)

    def compose(self) -> ComposeResult:
        with RadioSet():
            for i, rb in enumerate(self._radio_buttons):
                rb.BUTTON_INNER = "x"
                if i == self._default_choice:
                    rb.value = True
                yield rb

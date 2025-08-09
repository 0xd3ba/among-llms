from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Select

from allms.config import StyleConfiguration


class SelectComponent(Vertical):
    """ A generic class for selection list """

    def __init__(self, choices: list[str], title: str = "", default_choice: int = 0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.border_title = title
        select_choices = [(c,c) for c in choices]

        assert len(choices) > 0, f"For title={title}, the number of choices provided is 0"
        assert 0 <= default_choice < len(choices), f"Provided default choice({default_choice}) should be < # of choices ({len(choices)})"

        initial_value = choices[default_choice]
        self._selection_list = Select(options=select_choices, allow_blank=False, value=initial_value, compact=True)

    def on_mount(self) -> None:
        if self.border_title:
            self.add_class(StyleConfiguration.css_class_round_border)
            self.add_class(StyleConfiguration.css_class_highlight_border_on_focus)

    def compose(self) -> ComposeResult:
        yield self._selection_list

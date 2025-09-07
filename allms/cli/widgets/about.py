from textual.app import ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import MarkdownViewer

from allms.config import AppConfiguration, RunTimeConfiguration
from allms.core.state import GameStateManager
from .modal import ModalScreenWidget


_markdown_about = f"""\
# {AppConfiguration.app_name} v{AppConfiguration.app_version}

Just another chatroom ... or so it seems.  

At first, it’s only chatter. Then the room slowly darkens into a web of suspicion ... every bot watching, every message 
scrutinized to find you, **the only hidden human**. Any line of text can be your undoing. Every word is a clue, 
every silence a trap. One slip, and they’ll vote you out, ending you instantly. Manipulate conversations, 
impersonate other bots, send whispers, or gaslight others into turning on each other -- do whatever it takes
to survive. Chaos is your ally, deception your weapon. Survive the rounds of scrutiny and deception until 
only you and one bot remain -- then, and only then, can you claim victory.
 
> ### License
> {AppConfiguration.app_name} is released under GNU General Public License v3.0

> #### Found a bug/issue?
> Please create an issue at 
> `{AppConfiguration.app_repo}`
"""


class AboutAppWidget(ModalScreenWidget):

    def __init__(self, title: str, config: RunTimeConfiguration, state_manager: GameStateManager, *args, **kwargs):
        super().__init__(title, config, state_manager, *args, **kwargs)

    def compose(self) -> ComposeResult:
        yield MarkdownViewer(_markdown_about, show_table_of_contents=False)

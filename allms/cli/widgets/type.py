from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Label, LoadingIndicator

from allms.config import AppConfiguration


class ChatroomIsTyping(Container):
    """ Class for displaying typing status of agents """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._are_typing = set()
        self._typing_label = Label()
        self._loading_indicator = LoadingIndicator()

        # By default, hide them
        self._typing_label.display = False
        self._loading_indicator.display = False

    def compose(self) -> ComposeResult:
        with Horizontal(id="typing-indicator-container"):
            yield self._typing_label
            yield Label("  ")  # To ensure space is consumed
            yield self._loading_indicator

    def add_typing(self, agent_id: str) -> None:
        """ Adds the given agent to the typing set """
        self._are_typing.add(agent_id)
        self.__update_indicator()

    def remove_typing(self, agent_id: str) -> None:
        """ Removes the given agent from the typing set """
        if agent_id not in self._are_typing:
            AppConfiguration.logger.log(f"Trying to remove {agent_id} from typing set but it doesn't exist in it: {self._are_typing}")
            return

        self._are_typing.remove(agent_id)
        self.__update_indicator()

    def remove_all(self) -> None:
        """ Removes all the agents from the typing set """
        self._are_typing.clear()
        self.__update_indicator()

    def __update_indicator(self) -> None:
        """ Helper method to update the loading indicator """
        typing_str = self.__create_is_typing_text()
        if not typing_str:
            self._typing_label.display = False
            self._loading_indicator.display = False
        else:
            self._typing_label.update(typing_str)
            self._typing_label.display = True
            self._loading_indicator.display = True

    def __create_is_typing_text(self, max_agents: int = 3) -> str:
        """ Helper method to create the text that the agents are typing """
        if not self._are_typing:
            return ""

        agents = sorted(list(self._are_typing))
        n_agents_typing = len(agents)

        if n_agents_typing == 1:
            return f"{agents[0]} is typing"

        elif n_agents_typing <= max_agents:
            names_str = ", ".join(agents[:-1]) + f" and {agents[-1]}"
            return f"{names_str} are typing"

        # More than max_agents are typing
        else:
            others_count = n_agents_typing - 1
            return f"{agents[0]} and {others_count} others are typing"

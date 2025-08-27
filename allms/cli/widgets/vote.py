from typing import Optional

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import Button, Label, RadioButton, RadioSet, Static

from allms.config import RunTimeConfiguration
from allms.core.state import GameStateManager
from .modal import ModalScreenWidget


class _RadioSetComponent(RadioSet):
    def __init__(self, agent_ids: list[str], can_vote: bool, default_choice: Optional[str], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._agent_ids = agent_ids
        self._can_vote = can_vote
        self._default_choice = default_choice
        self._radio_buttons = [RadioButton(agent_id) for agent_id in agent_ids]

    def compose(self) -> ComposeResult:
        # Map the default choice to index
        def_choice_idx = 0
        if self._default_choice is not None:
            def_choice_idx = self._agent_ids.index(self._default_choice)

        for i, rb in enumerate(self._radio_buttons):
            rb.BUTTON_INNER = "x"
            if not self._can_vote:
                rb.disabled = True
            if i == def_choice_idx:
                rb.value = True

            yield rb

    def disable_choices(self) -> None:
        """ Disables all the radio button choices """
        for rb in self._radio_buttons:
            rb.disabled = True


class VotingWidget(ModalScreenWidget):

    def __init__(self, title: str, config: RunTimeConfiguration, state_manager: GameStateManager, *args, **kwargs):
        super().__init__(title, config, state_manager, *args, **kwargs)
        self._your_id = state_manager.get_user_assigned_agent_id()
        self._remaining_ids = self._state_manager.get_all_remaining_agents_ids()
        self._default_choice: Optional[str] = self._state_manager.get_voted_for_who(self._your_id)

        # User if allowed to vote if voting has not started yet (starts a new vote), or they didn't vote yet
        vote_started_yet, _ = state_manager.voting_has_started()
        self._can_vote = (not vote_started_yet) or state_manager.can_vote(self._your_id)
        self._voting_for: Optional[str] = None

        self._id_btn_confirm = "voting-confirm-btn"
        self._id_btn_cancel = "voting-cancel-btn"

        voted_for = state_manager.get_voted_for_who(by_agent=self._your_id)
        self._info_text = "[b]Note[/]: You are allowed to vote [i]only once[/] per session"
        if voted_for is not None:
            self._info_text = f"You voted for [bold italic]{voted_for}[/]"

    def compose(self) -> ComposeResult:
        radio_set = _RadioSetComponent(self._remaining_ids, can_vote=self._can_vote, default_choice=self._default_choice)
        confirm_btn, cancel_btn = self._create_confirm_cancel_buttons(self._id_btn_confirm, self._id_btn_cancel)

        main_container_title = f"Who's the Human ? (Hint: {self._your_id})"

        with VerticalScroll():
            yield self._wrap_inside_container(radio_set, Horizontal, border_title=main_container_title, cid="voting-radio-container")
            yield self._wrap_inside_container(Static(self._info_text), Horizontal, cid="voting-info-container")

        yield self._wrap_inside_container([cancel_btn, Label(" "), confirm_btn], Horizontal, cid="voting-buttons")

        radio_set.focus()

    @on(Button.Pressed)
    def handler_send_button_clicked(self, event: Button.Pressed) -> None:
        """ Handler invoked when send button is clicked """
        btn_id = event.button.id
        if btn_id == self._id_btn_confirm:
            self.__vote()
        elif btn_id == self._id_btn_cancel:
            pass
        else:
            # Should not come to this branch or else there is a bug
            raise RuntimeError(f"What button with id={btn_id} did you click in the voting screen")

        self.app.pop_screen()

    @on(RadioSet.Changed)
    def __update_voting_for_agent(self, event: RadioSet.Changed) -> None:
        """ Handler invoked when a different agent ID is selected """
        self._voting_for = event.pressed.label

    def __vote(self) -> None:
        """ Helper method to vote for the currently selected agent ID """
        assert self._voting_for is not None, f"Trying to vote for None. This should not happen"
        if not self._state_manager.voting_has_started()[0]:
            self._state_manager.start_vote(started_by=self._your_id)

        self._state_manager.vote(by_agent=self._your_id, for_agent=self._voting_for)

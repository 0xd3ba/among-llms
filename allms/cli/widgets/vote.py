from collections import OrderedDict
from typing import Optional

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import Button, Label, RadioButton, RadioSet, Select, Static

from allms.config import AppConfiguration, RunTimeConfiguration
from allms.core.state import GameStateManager
from .modal import ModalScreenWidget


class _RadioSetComponent(RadioSet):
    def __init__(self, agent_ids: list[str], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._agent_ids = agent_ids
        self._radio_buttons_map: OrderedDict[str, RadioButton] = OrderedDict()
        for agent_id in self._agent_ids:
            self._radio_buttons_map[agent_id] = RadioButton(agent_id)

    def compose(self) -> ComposeResult:
        for rb in self._radio_buttons_map.values():
            rb.BUTTON_INNER = "x"
            yield rb

    def update_state(self, agent_id: str, can_vote: bool, voted_for: Optional[str]) -> None:
        """ Updates the state of the buttons based on the given agent ID """
        assert agent_id in self._radio_buttons_map, f"Unknown agent {agent_id} while updating voting widget"
        # Agent is allowed to vote -- Voting has started and agent has not voted yet
        # or the voting has not started and agent is starting the vote
        if can_vote:
            assert voted_for is None, f"{agent_id} is allowed to vote when they already voted for {voted_for}. A bug."
            self._radio_buttons_map[agent_id].value = True  # Default choice is set to vote for themselves

        # Agent is not allowed to vote -- They have already provided their votes
        else:
            assert voted_for is not None, f"{agent_id} is not allowed to vote but they have not voted for anyone. A bug."
            assert voted_for in self._radio_buttons_map, f"{agent_id} voted to invalid agent: {voted_for}; not present in remaining ids"
            self._radio_buttons_map[voted_for].value = True
            self.__disable_choices()

    def __disable_choices(self) -> None:
        """ Helper method that disables all the radio button choices """
        for rb in self._radio_buttons_map.values():
            rb.disabled = True


class VotingWidget(ModalScreenWidget):

    def __init__(self, title: str, config: RunTimeConfiguration, state_manager: GameStateManager, *args, **kwargs):
        super().__init__(title, config, state_manager, *args, **kwargs)
        self._your_id = state_manager.get_user_assigned_agent_id()
        self._remaining_ids = self._state_manager.get_all_remaining_agents_ids()

        self._voting_as = self._your_id
        self._voting_for: Optional[str] = None

        self._id_btn_confirm = "voting-confirm-btn"
        self._id_btn_cancel = "voting-cancel-btn"

        # Note: There are some visual issues when changing from an agent X to different agent Y doesn't clear the visual
        # state of the radio-set (some buttons are still shown as set, especially when X had voted) no matter what you
        # do -- reset the buttons and then do refresh(), reset_styles(), _pressed_button=None etc.
        # Sometimes the approaches work, sometimes they don't. Very inconsistent behavior or maybe I don't know how to
        # handle this properly. Due to this, it's just better to create a radio-set per-agent instead and swap them
        # dynamically when agent is changed
        self._radio_widget_map: dict[str, Optional[_RadioSetComponent]] = {}
        self._radio_widget: Optional[_RadioSetComponent] = None
        self._radio_container: Optional[Container] = None
        self._select_widget: Optional[Select] = None
        self._info_widget: Optional[Static] = None
        self._default_info_text = "[b]Note[/]: You are allowed to vote [i]only once[/] per session"

    def compose(self) -> ComposeResult:
        agent_ids = [(aid, aid) for aid in self._remaining_ids]
        your_id = self._your_id
        can_vote, voted_for = self.__can_vote(your_id)
        info_text = self.__get_info_text(your_id)

        self._info_widget = Static(info_text)
        self._radio_widget_map = {agent_id: _RadioSetComponent(agent_ids=self._remaining_ids) for agent_id in self._remaining_ids}
        self._select_widget = Select(options=agent_ids, allow_blank=False, value=your_id, compact=True)
        confirm_btn, cancel_btn = self._create_confirm_cancel_buttons(self._id_btn_confirm, self._id_btn_cancel)

        main_container_title = f"Who's the Human ? (Hint: {your_id})"
        self._radio_widget = self._radio_widget_map[your_id]
        self._radio_widget.update_state(agent_id=your_id, can_vote=can_vote, voted_for=voted_for)
        self._radio_container = self._wrap_inside_container(self._radio_widget, Horizontal, border_title=main_container_title, cid="voting-radio-container")

        with VerticalScroll():
            yield self._wrap_inside_container(self._select_widget, Horizontal, border_title="Vote As", cid="voting-vote-as")
            yield self._radio_container
        yield self._wrap_inside_container(self._info_widget, Horizontal, cid="voting-info-container")
        yield self._wrap_inside_container([cancel_btn, Label(" "), confirm_btn], Horizontal, cid="voting-buttons")

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
        self._voting_for = str(event.pressed.label)

    @on(Select.Changed)
    async def __update_voting_as(self, event: Select.Changed) -> None:
        """ Handler invoked when a different agent ID is selected """
        # Note: Need to make this async or else the first time voting screen is shown,
        # the voting widget is not rendered to the screen unless you select a different agent from the selection
        # list, after which it works normally. Awaiting ensures it is rendered to the screen
        self._voting_as = event.select.value

        # Update the voting buttons (enable/disable them)
        can_vote, voted_for = self.__can_vote(self._voting_as)
        AppConfiguration.logger.log(f"You ({self._your_id}) will now be voting as [{self._voting_as}], "
                                    f"can_vote={can_vote}, voted_for={voted_for}")

        # Unmount current radio widget and swap it with the corresponding agent's widget
        await self._radio_widget.remove()
        self._radio_widget = self._radio_widget_map[self._voting_as]
        self._radio_widget.update_state(agent_id=self._voting_as, can_vote=can_vote, voted_for=voted_for)

        await self._radio_container.mount(self._radio_widget)

        # Update the info text
        info_text = self.__get_info_text(self._voting_as)
        self._info_widget.update(info_text)
        self._radio_widget.focus()

    def __vote(self) -> None:
        """ Helper method to vote for the currently selected agent ID """
        assert self._voting_for is not None, f"Trying to vote for None. This should not happen"
        agent_id = self._voting_as
        if not self._state_manager.voting_has_started()[0]:
            self._state_manager.start_vote(started_by=agent_id, started_by_you=True)

        self._state_manager.vote(by_agent=agent_id, for_agent=self._voting_for, voting_by_you=True)

    def __can_vote(self, agent_id: str) -> tuple[bool, str]:
        """
        Helper method that returns (True, None) if the agent is allowed to vote,
        else (False, agent_id) if vote started already and the agent has voted
        """
        # User is allowed to vote if voting has not started yet (starts a new vote), or they didn't vote yet
        vote_started_yet, _ = self._state_manager.voting_has_started()
        can_vote = (not vote_started_yet) or self._state_manager.can_vote(agent_id)
        voted_for = self._state_manager.get_voted_for_who(agent_id)

        return can_vote, voted_for

    def __get_info_text(self, agent_id: str) -> str:
        """ Helper method to prepare the info text and returns the text """
        voted_for = self._state_manager.get_voted_for_who(by_agent=agent_id)
        info_text = self._default_info_text
        if voted_for is not None:
            info_text = f"You voted for [bold italic]{voted_for}[/]"

        return info_text

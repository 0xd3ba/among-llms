import logging
from collections import Counter
from dataclasses import dataclass, field
from typing import Optional

from allms.config import AppConfiguration


@dataclass
class _VoteResult:
    """ Class for the result of the vote """
    # Mapping between an agent ID and the number of votes they received
    __vote_count: Counter[str] = field(default_factory=dict)

    def get_results(self) -> Counter:
        """ Returns the voting results as a map between agent ID and the number of votes received """
        return self.__vote_count.copy()

    def prepare_result(self, vote_map: dict[str, str]) -> None:
        """ Method for preparing the voting result """
        assert len(vote_map) > 0, f"Received no votes"
        self.__vote_count = Counter(vote_map.values())


@dataclass
class AgentVoting:
    # Mapping between an agent ID and the agent they voted for
    _vote_map: dict[str, str] = field(default_factory=dict)
    _vote_has_started: bool = False
    _started_by: Optional[str] = None

    def voting_has_started(self) -> tuple[bool, Optional[str]]:
        return self._vote_has_started, self._started_by

    def total_voters(self) -> int:
        """ Returns the total number of voters so far """
        return len(self._vote_map)

    def start_vote(self, started_by: str) -> None:
        """ Starts the voting process """
        if not self._vote_has_started:
            AppConfiguration.logger.log(f"-- Voting process has been started by {started_by} --")
            self._vote_has_started = True
            self._started_by = started_by
            self._vote_map.clear()
        else:
            AppConfiguration.logger.log(f"Trying to start a vote by {started_by} which was already started " +
                                        f"previously by {started_by}", level=logging.WARNING)

    def vote(self, by_agent: str, for_agent: str) -> bool:
        """ Vote by an agent (by_agent) for a specific agent (for_agent). Returns True if vote was successful. """
        if self.can_vote(by_agent):
            AppConfiguration.logger.log(f"{by_agent} is voting for {for_agent}")
            self._vote_map[by_agent] = for_agent
            return True
        return False

    def get_voted_for_who(self, by_agent: str) -> Optional[str]:
        """ Returns the ID of the agent that the given agent voted for (if any), else None """
        if self._vote_has_started:
            return self._vote_map.get(by_agent, None)
        return None

    def get_who_voted_and_for_whom(self) -> list[tuple[str, str]]:
        """
        Returns a list of tuples of the agents who voted (and for whom). Each item is of form:
            (who_voted, voted_for_whom)
        """
        vote_list = [(k, v) for (k, v) in self._vote_map.items()]
        return vote_list

    def end_vote(self) -> Counter:
        """
        Ends the voting process and returns the voting results as a mapping:
            {agent_id: number_of_votes_received}
        """
        assert self._vote_has_started, f"Trying to end a vote which did not even begun"

        AppConfiguration.logger.log(f"-- Voting process has ended --")
        self._vote_has_started = False
        result = _VoteResult()
        result.prepare_result(self._vote_map)

        return result.get_results()

    def can_vote(self, by_agent: str) -> bool:
        """ Returns True if the given agent is allowed to vote """
        if by_agent in self._vote_map:
            return False
        if not self._vote_has_started:
            AppConfiguration.logger.log(f"Voting has not started yet (or ended) and {by_agent} is trying to vote")

        return self._vote_has_started

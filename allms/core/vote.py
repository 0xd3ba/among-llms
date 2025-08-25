import logging
from collections import Counter
from dataclasses import dataclass, field

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
    __vote_map: dict[str, str] = field(default_factory=dict)
    __vote_has_started: bool = False

    def voting_is_in_progress(self) -> bool:
        return self.__vote_has_started

    def start_vote(self) -> None:
        """ Starts the voting process """
        AppConfiguration.logger.log(f"-- Voting process has started --")
        self.__vote_has_started = True
        self.__vote_map.clear()

    def vote(self, by_agent: str, for_agent: str) -> None:
        if self.__can_vote(by_agent):
            AppConfiguration.logger.log(f"{by_agent} is voting for {for_agent}")
            self.__vote_map[by_agent] = for_agent

    def end_vote(self) -> Counter:
        """
        Ends the voting process and returns the voting results as a mapping:
            {agent_id: number_of_votes_received}
        """
        assert self.__vote_has_started, f"Trying to end a vote which did not even begun"

        AppConfiguration.logger.log(f"-- Voting process has ended --")
        self.__vote_has_started = False
        result = _VoteResult()
        result.prepare_result(self.__vote_map)

        return result.get_results()

    def __can_vote(self, by_agent: str) -> bool:
        """ Returns True if the given agent is allowed to vote """
        if by_agent in self.__vote_map:
            AppConfiguration.logger.log(f"{by_agent} already voted previously and trying to vote again")
            return False
        if not self.__vote_has_started:
            AppConfiguration.logger.log(f"Voting has not started yet and {by_agent} is trying to vote")

        return self.__vote_has_started

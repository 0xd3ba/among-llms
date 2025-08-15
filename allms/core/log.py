from dataclasses import dataclass, field


@dataclass
class GameEvent:
    timestamp: str
    event: str


@dataclass
class GameEventLogs:
    """ Class storing the runtime logs """
    # List of all the game logs
    _logs: list[GameEvent] = field(default_factory=list)

    def add(self, event: GameEvent) -> None:
        """ Adds the event to the log """
        self._logs.append(event)

    def get(self) -> list[GameEvent]:
        """ Returns the current state of the game logs """
        return self._logs.copy()

    # TODO: Register a signal or something to update the logs in the UI later on -- Think about the design later

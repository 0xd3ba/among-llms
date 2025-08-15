from dataclasses import dataclass, field


@dataclass
class Agent(frozenset=True):
    """ Class for an agent """
    id: str       # The unique identifier of the agent
    persona: str  # The persona assigned to the agent

    # List of message IDs of the messages sent by the agent
    msg_ids: set[str] = field(default_factory=list)

    def add_message_id(self, msg_id: str) -> None:
        """ Adds the message ID to the list of IDs sent by the agent """
        if msg_id not in self.msg_ids:
            self.msg_ids.add(msg_id)

    def get_message_ids(self) -> list[str]:
        """ Returns a sorted list of all the message IDs of the messages sent by the agent """
        return sorted(list(self.msg_ids))

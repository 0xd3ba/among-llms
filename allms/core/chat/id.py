from dataclasses import dataclass


@dataclass
class ChatMessageIDGenerator:
    """ Message ID generator class """
    _id: int = 0     # The start value of ID

    def initialize_id(self, i: int) -> None:
        """ Initializes the ID to the given value """
        self._id = i

    def next(self) -> str:
        """ Returns the next available message id """
        msg_id = self._id
        self._id += 1
        return str(msg_id)

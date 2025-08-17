from dataclasses import dataclass, field
from threading import Lock


@dataclass
class ChatMessageIDGenerator:
    """ Message ID generator class """
    _start_id: int = 0     # The start value of ID
    _lock: Lock = Lock()   # Mutex to ensure no race-condition
    # Side-note: There is an alternative fast way to ensure race-free situations using
    # itertools.count but that relies on GIL which may or may not be present in other python
    # implementations, so I'm hesitant to use it. Since the number of agents will be very less and
    # generating message id will be every few seconds, there will probably be no visible performance
    # impact caused due to using a lock for this

    def next(self) -> str:
        """ Returns the next available message id """
        with self._lock:
            msg_id = self._start_id
            self._start_id += 1
            return str(msg_id)

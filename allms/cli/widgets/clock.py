from textual.app import ComposeResult
from textual.widgets import Static

from allms.config import AppConfiguration


class ChatClock(Static):
    """ Class for the clock widget """

    def __init__(self):
        super().__init__()
        self._update_time()

    def on_mount(self) -> None:
        self._update_time()
        self.set_interval(1.0, self._update_time)

    def _update_time(self) -> None:
        """ Method to update the timestamp on every call """
        # Timestamp format: Mon 28 Apr 2025, 13:54:47
        time = AppConfiguration.clock.current_timestamp_in_given_format("%a %d %B %Y, %H:%M:%S")
        self.update(time)

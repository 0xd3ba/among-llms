from textual.widgets import Static

from allms.utils.time import Time


class ClockWidget(Static):
    """ Class for the clock widget """

    def __init__(self, clock: Time):
        super().__init__()
        self._clock = clock

    def on_mount(self) -> None:
        self._update_time()
        self.set_interval(1.0, self._update_time)

    def _update_time(self) -> None:
        """ Method to update the timestamp on every call """
        # Example timestamp format: Mon 28 Apr 2025, 13:54:47 EDT
        time = self._clock.current_timestamp_in_given_format("%a %d %B %Y, %H:%M:%S %Z")
        self.update(time)

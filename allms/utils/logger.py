import logging
from pathlib import Path
from typing import Optional

from .time import Time


class AppLogger:
    """ Class to create a global logger """

    def __init__(self, log_dir: str | Path, clock: Time, log_level: int = logging.DEBUG):
        self._log_dir = log_dir
        self._clock = clock
        self._log_level = log_level

        self._file_handler: Optional[logging.FileHandler] = None
        self._stream_handler: Optional[logging.StreamHandler] = None
        self._logger: Optional[logging.Logger] = None

        self.__create_logger(log_dir, clock, log_level)

    def log(self, msg: str, level: int | str = ""):
        """ Method to log the output to the log file / console stream"""
        if not level:
            level = self._log_level
        self._logger.log(level, msg=msg)

    def set_log_level(self, level: int) -> None:
        """ Sets the log level for the logger """
        self.__create_logger(self._log_dir, self._clock, level)

    def remove_handler_of_console_stream(self) -> None:
        """ Removes the handler of the console stream """
        if self._stream_handler in self._logger.handlers:
            self._logger.removeHandler(self._stream_handler)

    def add_handler_of_console_stream(self) -> None:
        """ Adds teh handler of the console stream """
        if self._stream_handler not in self._logger.handlers:
            self._logger.addHandler(self._stream_handler)

    def __create_logger(self,
                        log_dir: str | Path,
                        clock: Time,
                        log_level: int = logging.DEBUG) -> None:
        """ Helper method to create and configure a logger """

        if isinstance(log_dir, str):
            log_dir = Path(log_dir)

        log_dir.mkdir(parents=True, exist_ok=True)
        assert log_dir.is_dir(), f"Provided path must be a valid directory"

        curr_ts = clock.current_timestamp_in_iso_format()
        curr_ts = clock.convert_to_snake_case(curr_ts)
        log_file = f"{curr_ts}.log"
        log_path = log_dir / log_file

        logger = logging.getLogger()
        file_handler = logging.FileHandler(log_path)
        stream_handler = logging.StreamHandler()

        formatter = logging.Formatter(fmt="%(asctime)s [%(levelname)s] %(message)s")

        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

        logger.setLevel(log_level)

        self._file_handler = file_handler
        self._stream_handler = stream_handler
        self._logger = logger


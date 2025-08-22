import logging
from pathlib import Path

from .time import Time


class AppLogger:
    """ Class to create a global logger """

    @staticmethod
    def create_logger(log_dir: str | Path,
                      clock: Time,
                      log_level: int = logging.DEBUG) -> logging.Logger:
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
        formatter = logging.Formatter(fmt="%(asctime)s [%(levelname)s] %(message)s")

        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.setLevel(log_level)

        return logger

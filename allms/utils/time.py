import pandas as pd
from textual import log


class Time:
    """ A handy class for custom date/time manipulation """

    def __init__(self, timezone: str):
        self._timezone = timezone

    @staticmethod
    def current_timestamp_in_milliseconds_utc() -> int:
        """ Returns the current time in milliseconds (in UTC) """
        ts = pd.to_datetime("now", utc=True)
        val_ns = ts.value         # Time in UNIX nanoseconds
        val_ms = val_ns // 10**6  # Convert to milliseconds

        return val_ms

    def current_timestamp_in_iso_format(self) -> str:
        """ Returns the current timestamp in ISO format """
        ms = self.current_timestamp_in_milliseconds_utc()
        return self.milliseconds_to_iso_format(ms)

    def current_timestamp_in_given_format(self, fmt: str) -> str:
        """ Returns the current timestamp in specified format """
        now = pd.Timestamp.now(tz=self._timezone)
        return now.strftime(fmt)

    def current_date_in_iso_format(self) -> str:
        """ Returns the current date in ISO format (yyyy-mm-dd) """
        ms = self.current_timestamp_in_milliseconds_utc()
        return self.date(ms)
    
    def current_time_in_iso_format(self) -> str:
        """ Returns the current time in ISO format (hh:mm:ss) """
        ms = self.current_timestamp_in_milliseconds_utc()
        return self.time(ms)

    def date(self, milliseconds: int | str, in_utc: bool = False) -> str:
        """ Given a timestamp in UNIX milliseconds (UTC), returns the date (in local timezone if "in_utc" is False) """
        ts = self.timestamp(milliseconds, in_utc)
        date = ts.date().isoformat()
        return date

    def time(self, milliseconds: int | str, in_utc: bool = False) -> str:
        """ Given a timestamp in UNIX milliseconds (UTC), returns the time (in local timezone if "in_utc" is False) """
        ts = self.timestamp(milliseconds, in_utc)
        time = ts.time().isoformat()
        return time

    def milliseconds_to_iso_format(self, milliseconds: int | str, in_utc: bool = False) -> str:
        """ Given a timestamp in UNIX milliseconds (UTC), returns the time (in local timezone if "in_utc" is False) """
        date = self.date(milliseconds, in_utc)
        time = self.time(milliseconds, in_utc)

        # Returns a string in ISO format: "YYYY-MM-DD HH:MM:SS"
        return f"{date} {time}"
    
    def iso_format_to_milliseconds(self, date_time_iso: str) -> int:
        """
        Given a date and time string in ISO format (YYYYY-MM-DD HH:MM:SS), converts it back to UNIX milliseconds in UTC
        """
        ts_local = pd.to_datetime(date_time_iso).tz_localize(self._timezone)
        ts_utc = ts_local.tz_convert("UTC")
        utc_ms = int(ts_utc.timestamp() * 1000)   # Need to convert seconds to milliseconds
        return utc_ms
    
    def calculate_duration(self, end_ts_ms: int, start_ts_ms: int) -> tuple[float | int, str]:
        """
        Calculates the duration between the end timestamp (in ms) and start timestamp (in ms)
        and returns the duration (in milliseconds, seconds, minutes, hours, days)
        """
        duration = end_ts_ms - start_ts_ms
        second = 1_000        # 1s = 1000ms
        minute = second * 60  # 1m = 60 * 1000ms
        hour = minute * 60    # 1h = 60 * 60 * 1000ms
        day = hour * 24       # 1d = 24 * 60 * 60 * 1000ms

        if duration < second:
            divider = 1
            unit = "milliseconds"

        elif duration < minute:
            divider = second
            unit = "seconds"

        elif duration < hour:
            divider = minute
            unit = "minutes"

        elif duration < day:
            divider = hour
            unit = "hours"

        else:
            divider = day
            unit = "days"

        duration = round(duration / divider, 2)
        return duration, unit

    def add_n_days(self, milliseconds: int | str, n_days: int) -> int:
        """
        Adds N days to the given timestamp in UNIX milliseconds (UTC) and returns the resulting timestamp, also
        in UNIX milliseconds (UTC)
        """
        n_hours = n_days * 24
        return self.add_n_hours(milliseconds, n_hours)

    def add_n_hours(self, milliseconds: int | str, n_hours: int) -> int:
        """
        Adds N hours to the given timestamp in UNIX milliseconds (UTC) and returns the resulting timestamp, also
        in UNIX milliseconds (UTC)
        """
        n_minutes = n_hours * 60
        return self.add_n_minutes(milliseconds, n_minutes)

    def add_n_minutes(self, milliseconds: int | str, n_minutes: int) -> int:
        """
        Adds N minutes to the given timestamp in UNIX milliseconds (UTC) and returns the resulting timestamp, also
        in UNIX milliseconds (UTC)
        """
        ts = self.timestamp(milliseconds, in_utc=True)
        delta = pd.Timedelta(minutes=n_minutes)

        new_ts = ts + delta
        val_ns = new_ts.value     # The result is in nanoseconds
        val_ms = val_ns // 10**6  # Convert to milliseconds

        return val_ms

    def timestamp(self, milliseconds: int | str, in_utc: bool = False) -> pd.Timestamp:
        """ Given a timestamp in UNIX milliseconds (UTC), returns a pandas Timestamp """
        ms = int(milliseconds) if isinstance(milliseconds, str) else milliseconds
        ts = pd.to_datetime(ms, unit="ms", utc=True)
        if not in_utc:
            ts = ts.tz_convert(self._timezone)

        return ts.floor("s")  # Round-up to seconds precision

    def convert_to_snake_case(self, date_or_time: str) -> str:
        """
        Returns the given date or/and time string in ISO format to snake-case
        For example,
            input:  2025-02-11 12:23:00
            output: 20250211_122300
        """
        fmt_str = date_or_time.replace("-", "")
        fmt_str = fmt_str.replace(":", "")
        fmt_str = "_".join(fmt_str.split(" "))

        return fmt_str

    def convert_from_snakecase(self, date_or_time: str) -> str:
        """
        Returns the previously snake-case converted date/time string to ISO format
        For example,
            input:   20250211_122300
            output:  2025-02-11 12:23:00
        """

        def _convert_back_to_iso(fmt_str: str, is_date: bool) -> str:
            """ Helper method to convert the given string (either date or time) to ISO format """
            if is_date:
                iso_str = f"{fmt_str[:4]}-{fmt_str[4:6]}-{fmt_str[6:8]}"
            else:
                iso_str = f"{fmt_str[:2]}:{fmt_str[2:4]}:{fmt_str[4:6]}"

            return iso_str

        date_len = 8  # YYYYMMDD format string
        time_len = 6  # HHMMSS format string
        invalid_str_msg = f"Invalid string provided: {date_or_time}. Need to be in the following format: " + \
                          f"YYYYMMDD_HHMMSS. Example: 20250211_122300"

        if "_" in date_or_time:
            date, time = date_or_time.split("_")
            if (len(date) == date_len) and (len(time) == time_len):
                date = _convert_back_to_iso(date, is_date=True)
                time = _convert_back_to_iso(time, is_date=False)
                date_time_iso = date + " " + time
            else:
                log.error(invalid_str_msg)
                raise RuntimeError

        elif len(date_or_time) == date_len:
            date_time_iso = _convert_back_to_iso(date_or_time, is_date=True)

        elif len(date_or_time) == time_len:
            date_time_iso = _convert_back_to_iso(date_or_time, is_date=False)
        else:
            log.error(invalid_str_msg)
            raise RuntimeError

        return date_time_iso

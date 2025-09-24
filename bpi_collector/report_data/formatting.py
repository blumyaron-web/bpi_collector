from .timestamp_utils import convert_timestamp_to_datetime, convert_utc_to_local


def format_timestamp(ts) -> str:
    dt = convert_timestamp_to_datetime(ts)
    local_dt = convert_utc_to_local(dt)
    return local_dt.strftime("%Y-%m-%d %I:%M:%S %p")


def format_time_short(ts) -> str:
    dt = convert_timestamp_to_datetime(ts)
    local_dt = convert_utc_to_local(dt)
    return local_dt.strftime("%I:%M %p")


def calculate_duration(start_ts, end_ts) -> str:
    start_dt = convert_timestamp_to_datetime(start_ts)
    end_dt = convert_timestamp_to_datetime(end_ts)

    duration = end_dt - start_dt
    hours, remainder = divmod(duration.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)

    if hours > 0:
        return f"{int(hours)}h {int(minutes)}m"
    elif minutes > 0:
        return f"{int(minutes)}m {int(seconds)}s"
    else:
        return f"{int(seconds)}s"

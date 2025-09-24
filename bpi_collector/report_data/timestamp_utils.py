from zoneinfo import ZoneInfo
from datetime import datetime, timezone
from typing import Union, List, Dict, Any, Tuple


def convert_timestamp_to_datetime(ts: Union[str, datetime]) -> datetime:
    if isinstance(ts, str):
        if ts.endswith("Z"):
            return datetime.fromisoformat(ts.replace("Z", "+00:00"))
        else:
            return datetime.fromisoformat(ts)
    else:
        return ts


def convert_utc_to_local(dt: Union[str, datetime]) -> datetime:
    if isinstance(dt, str):
        dt = convert_timestamp_to_datetime(dt)

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    # Use the local system timezone instead of hardcoding a specific timezone
    local_dt = dt.astimezone()
    return local_dt


def format_datetime_local(
    dt: Union[str, datetime], include_seconds: bool = True
) -> str:
    local_dt = convert_utc_to_local(dt)

    if include_seconds:
        return local_dt.strftime("%Y-%m-%d %I:%M:%S %p")
    else:
        return local_dt.strftime("%Y-%m-%d %I:%M %p")


def extract_price_stats(
    samples: List[Dict[str, Any]], pair: str
) -> Tuple[float, float, float, float]:
    prices = []
    for s in samples:
        if s.get("prices") and s.get("prices").get(pair) is not None:
            prices.append(s["prices"][pair])

    if not prices:
        return 0, 0, 0, 0

    min_price = min(prices)
    max_price = max(prices)
    current = prices[-1]
    change = ((current - prices[0]) / prices[0] * 100) if prices[0] else 0

    return min_price, max_price, current, change

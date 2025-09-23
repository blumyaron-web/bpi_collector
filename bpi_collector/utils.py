from typing import List, Dict, Any, Optional, Tuple


def get_price_statistics(
    samples: List[Dict[str, Any]], currencies: Optional[list] = None
) -> Tuple[str, Optional[float]]:
    if not samples:
        return "BTC-USD", None

    first_sample_prices = samples[0].get("prices") or {}
    if first_sample_prices:
        first_pair = list(first_sample_prices.keys())[0]

    else:
        first_pair = currencies[0] if currencies else "BTC-USD"

    vals = [
        s.get("prices", {}).get(first_pair)
        for s in samples
        if s.get("prices") and s.get("prices").get(first_pair) is not None
    ]

    max_price = max(vals, default=None)
    return first_pair, max_price


def validate_smtp_config(config: dict) -> bool:
    required_keys = ["server", "username", "password", "to"]
    return all([config.get(key) for key in required_keys])

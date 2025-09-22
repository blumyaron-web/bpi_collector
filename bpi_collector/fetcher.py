import requests
from .config import Config
from .logger import BusinessLogicLogger


class DataFetcher:
    def __init__(self, config: Config, logger: BusinessLogicLogger):
        self.config = config
        self.logger = logger

    def fetch_prices(self) -> dict:
        """Fetch all configured currency pairs. Returns {pair: price} dict."""
        pairs = self.config.currencies or ["BTC-USD"]
        results = {}
        for p in pairs:
            url = self.config.api_url_template.format(pair=p)
            try:
                self.logger.info("Fetching price", pair=p, url=url)
                resp = requests.get(url, timeout=15)
                resp.raise_for_status()
                data = resp.json()
                amount = float(data['data']['amount'])
                results[p] = amount
                self.logger.info("Fetched price", pair=p, price=amount)
            except Exception as e:
                self.logger.error("Failed to fetch price", pair=p, error=str(e))
        return results

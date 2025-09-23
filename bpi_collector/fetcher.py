import requests
from .config import Config
from logging import Logger


class DataFetcher:
    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger

    def fetch_prices(self) -> dict:
        pairs = self.config.currencies or ["BTC-USD"]
        results = {}
        for pair in pairs:
            url = self.config.api_url_template.format(pair=pair)

            try:
                self.logger.info(f"Fetching price {pair}\n{url}")
                resp = requests.get(url, timeout=15)
                resp.raise_for_status()
                data = resp.json()
                amount = float(data["data"]["amount"])

                results[pair] = amount
                self.logger.info(f"Fetched price {pair}\nprice:{amount}")

            except Exception as e:
                self.logger.error(f"Failed to fetch price {pair} {e}")

        return results

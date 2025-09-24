import time
from .config import Config
from logging import Logger
from .storage import Storage
from datetime import datetime, timezone
from .fetcher import DataFetcher
from .grapher import GraphGenerator


class BPICollector:
    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger
        self.fetcher = DataFetcher(config, logger)
        self.storage = Storage(config.store_path, logger)
        self.grapher = GraphGenerator(config.graph_path, logger)

    def run_once(self) -> dict:
        prices = self.fetcher.fetch_prices()
        # Use timezone-aware UTC time with Z suffix
        now = datetime.now(timezone.utc)
        self.storage.append_sample(now, prices)
        return prices

    def run_loop(self):
        self.logger.info(
            f"Starting collection loop {self.config.samples}\n{self.config.interval_seconds}",
        )
        for i in range(self.config.samples):
            try:
                self.run_once()
            except Exception as e:
                self.logger.error(f"Sample failed\n{e}")

            if i < self.config.samples - 1:
                time.sleep(self.config.interval_seconds)

        samples = self.storage.read_all()
        self.grapher.generate(samples)
        return samples

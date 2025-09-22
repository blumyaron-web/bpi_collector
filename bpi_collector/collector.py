import time
from datetime import datetime
from .config import Config
from .logger import BusinessLogicLogger
from .fetcher import DataFetcher
from .storage import Storage
from .grapher import GraphGenerator


class BPICollector:
    def __init__(self, config: Config, logger: BusinessLogicLogger):
        self.config = config
        self.logger = logger
        self.fetcher = DataFetcher(config, logger)
        self.storage = Storage(config.store_path, logger)
        self.grapher = GraphGenerator(config.graph_path, logger)

    def run_once(self) -> dict:
        prices = self.fetcher.fetch_prices()
        self.storage.append_sample(datetime.utcnow(), prices)
        return prices

    def run_loop(self):
        self.logger.info("Starting collection loop", samples=self.config.samples, interval=self.config.interval_seconds)
        for i in range(self.config.samples):
            try:
                self.run_once()
            except Exception as e:
                self.logger.error("Sample failed", error=str(e))
            if i < self.config.samples - 1:
                time.sleep(self.config.interval_seconds)
        samples = self.storage.read_all()
        self.grapher.generate(samples)
        return samples

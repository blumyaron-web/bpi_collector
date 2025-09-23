import sys
import logging


class BusinessLogicLogger:
    def __init__(self, name: str = "bpi_collector"):
        self.logger = logging.getLogger(name)
        if not self.logger.handlers:
            h = logging.StreamHandler(sys.stdout)
            fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
            h.setFormatter(fmt)
            self.logger.addHandler(h)
            self.logger.setLevel(logging.INFO)


logger = BusinessLogicLogger().logger

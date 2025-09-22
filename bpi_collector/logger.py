import logging
import sys

class BusinessLogicLogger:
    def __init__(self, name: str = 'bpi_bl'):
        self.logger = logging.getLogger(name)
        if not self.logger.handlers:
            h = logging.StreamHandler(sys.stdout)
            fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
            h.setFormatter(fmt)
            self.logger.addHandler(h)
            self.logger.setLevel(logging.INFO)

    def info(self, msg: str, **kwargs):
        try:
            self.logger.info(msg, extra={**kwargs})
        except Exception:
            self.logger.info(msg)

    def error(self, msg: str, **kwargs):
        try:
            self.logger.error(msg, extra={**kwargs})
        except Exception:
            self.logger.error(msg)

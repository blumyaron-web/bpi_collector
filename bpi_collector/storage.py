import os
import json

from logging import Logger
from datetime import datetime
from typing import List, Dict, Any


class Storage:
    def __init__(self, path: str, logger: Logger):
        self.path = path
        self.logger = logger

    def append_sample(self, timestamp: datetime, prices: dict):
        entry = {"ts": timestamp.isoformat(), "prices": prices}
        data = []
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as err:
                self.logger.error(
                    f"Failed to read existing storage file; starting fresh\n{err}"
                )
                data = []

        data.append(entry)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        self.logger.info(f"Appended sample {entry}")

    def read_all(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.path):
            return []
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

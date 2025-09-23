import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as m_tick
import matplotlib.dates as m_dates

from logging import Logger
from typing import List, Dict, Any
from datetime import datetime, timezone


class GraphGenerator:
    def __init__(self, graph_path: str, logger: Logger):
        self.logger = logger
        self.graph_path = graph_path

    def generate(self, samples: List[Dict[str, Any]]):
        if not samples:
            self.logger.error("No samples to graph")
            return

        times = [
            datetime.fromisoformat(s["ts"]).replace(tzinfo=timezone.utc).astimezone()
            for s in samples
        ]
        first_prices = samples[0].get("prices", {}) if samples else {}
        pairs = list(first_prices.keys())

        fig, ax = plt.subplots(figsize=(10, 4))
        for pair in pairs:
            series = [s["prices"].get(pair, None) for s in samples]
            ax.plot(times, series, marker="o", label=pair)

        ax.set_title("Prices (last {} samples)".format(len(samples)))
        ax.set_xlabel("Time")
        ax.set_ylabel("Price")
        ax.grid(True)

        ax.ticklabel_format(useOffset=False, style="plain", axis="y")
        ax.yaxis.set_major_formatter(m_tick.StrMethodFormatter("{x:,.2f}"))

        annotation_threshold = 20
        if len(samples) <= annotation_threshold:
            for pair in pairs:
                series = [s["prices"].get(pair, None) for s in samples]
                for x, y in zip(times, series):
                    if y is not None:
                        ax.annotate(
                            f"{y:.2f}",
                            xy=(x, y),
                            xytext=(0, 6),
                            textcoords="offset points",
                            ha="center",
                            fontsize=8,
                        )

        ax.xaxis.set_major_formatter(m_dates.DateFormatter("%H:%M"))
        max_ticks = 8
        step = max(1, len(times) // max_ticks)
        tick_positions = [times[i] for i in range(0, len(times), step)]
        ax.set_xticks(tick_positions)

        if pairs:
            ax.legend(loc="upper left")

        fig.autofmt_xdate(rotation=30)
        fig.tight_layout()
        fig.savefig(self.graph_path)
        plt.close(fig)
        self.logger.info(f"Graph generated {self.graph_path}")

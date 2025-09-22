import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import matplotlib.dates as mdates
from datetime import datetime, timezone
from typing import List, Dict, Any
from .logger import BusinessLogicLogger


class GraphGenerator:
    def __init__(self, graph_path: str, logger: BusinessLogicLogger):
        self.graph_path = graph_path
        self.logger = logger

    def generate(self, samples: List[Dict[str, Any]]):
        if not samples:
            self.logger.error("No samples to graph")
            return
        # Parse timestamps (assumed stored as UTC naive) and convert to local timezone
        times = [datetime.fromisoformat(s['ts']).replace(tzinfo=timezone.utc).astimezone() for s in samples]
        # Determine currency pairs from the first sample
        pairs = []
        first_prices = samples[0].get('prices', {}) if samples else {}
        pairs = list(first_prices.keys())

        fig, ax = plt.subplots(figsize=(10, 4))
        for pair in pairs:
            series = [s['prices'].get(pair, None) for s in samples]
            ax.plot(times, series, marker='o', label=pair)
        ax.set_title('Prices (last {} samples)'.format(len(samples)))
        ax.set_xlabel('Time')
        ax.set_ylabel('Price')
        ax.grid(True)

        # Disable offset (so labels show full values) and force plain formatting
        ax.ticklabel_format(useOffset=False, style='plain', axis='y')
        ax.yaxis.set_major_formatter(mtick.StrMethodFormatter('{x:,.2f}'))

        # Annotate each point with its exact value (only when sample count is small)
        ANNOTATION_THRESHOLD = 20
        if len(samples) <= ANNOTATION_THRESHOLD:
            for pair in pairs:
                series = [s['prices'].get(pair, None) for s in samples]
                for x, y in zip(times, series):
                    if y is not None:
                        ax.annotate(f"{y:.2f}", xy=(x, y), xytext=(0, 6), textcoords='offset points', ha='center', fontsize=8)

        # Format x-axis as HH:MM to reduce clutter
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

        # Reduce tick density by showing every Nth tick (try to keep ~8 ticks)
        max_ticks = 8
        step = max(1, len(times) // max_ticks)
        tick_positions = [times[i] for i in range(0, len(times), step)]
        ax.set_xticks(tick_positions)

        # show legend for pairs
        if pairs:
            ax.legend(loc='upper left')

        fig.autofmt_xdate(rotation=30)
        fig.tight_layout()
        fig.savefig(self.graph_path)
        plt.close(fig)
        self.logger.info("Graph generated", path=self.graph_path)

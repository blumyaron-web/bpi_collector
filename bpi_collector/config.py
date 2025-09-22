from dataclasses import dataclass

API_URL_TEMPLATE = "https://api.coinbase.com/v2/prices/{pair}/spot"
DEFAULT_STORE = "bpi_data.json"
DEFAULT_GRAPH = "bpi_graph.png"


@dataclass
class Config:
    api_url_template: str = API_URL_TEMPLATE
    store_path: str = DEFAULT_STORE
    graph_path: str = DEFAULT_GRAPH
    interval_seconds: int = 60
    samples: int = 60
    # list of currency pairs to fetch, e.g. ["BTC-USD", "ETH-USD"]
    currencies: list[str] = None

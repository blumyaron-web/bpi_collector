
# BPI Collector

A Python utility that:
- Fetches cryptocurrency prices from Coinbase API (default: BTC-USD## Developer Notes

- Logging outputs to stdout at INFO level
- Run smoke tests with `--test` flag
- Future improvements:
  - Add unit tests
  - Implement CI/CD
  - Add rate limiting
  - Improve error handling

## License

This utility is for demonstration and light monitoring. Use responsibly and avoid excessive API polling.mestamped readings in JSON format
- Generates price trend graphs
- Sends email reports with maximum price and graph visualizations

The project supports multiple currency pairs and configurable sampling intervals.

## Project Structure

- `bpi_collector.py` — Main CLI entrypoint
- `bpi_collector/` — Core package modules:
    - `collector.py` — Main orchestrator for data collection and processing
    - `fetcher.py` — API interaction handler
    - `storage.py` — Data persistence manager
    - `grapher.py` — Graph generation using matplotlib
    - `emailer.py` — Email reporting system
    - `config.py` — Configuration management
    - `logger.py` — Business logic logging system
- `config.ini.sample` — SMTP configuration template
- `requirements.txt` — Project dependencies

## Quick Start

1. Set up Python environment:
```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

2. Configure email settings (optional):
```bash
cp config.ini.sample config.ini
# Edit config.ini with your SMTP details
```

3. Run the collector:
```bash
# Test run (single fetch)
python bpi_collector.py --test

# Full collection (60 samples, 1-minute intervals)
python bpi_collector.py

# Custom collection (10 samples, 5-second intervals)
python bpi_collector.py --samples 10 --interval 5

# Multiple currencies
python bpi_collector.py --pairs BTC-USD,ETH-USD
```

## Configuration

The program reads SMTP settings from `config.ini` (recommended). Copy the sample and edit values:

```bash
cp config.ini.sample config.ini
# edit config.ini and fill in the [smtp] section
```

Important keys in `[smtp]`:

- `server` — SMTP host (e.g. `smtp.gmail.com`)
- `port` — SMTP port (usually `587` for STARTTLS)
- `username` — SMTP login
- `password` — SMTP password or app password
- `from` — (optional) sender address (defaults to `username`)
- `to` — comma-separated recipient addresses

If `config.ini` or any setting is missing, the following environment variables are used as fallbacks (uppercase):

- `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `EMAIL_FROM`, `EMAIL_TO`

Gmail notes: if you use a Gmail account you will typically need to create an App Password (or enable a less secure option where supported). Use the App Password in `smtp.password`.

## How it works (high level)

1. `BPICollector` performs repeated fetches using `DataFetcher`.
2. Each sample ({timestamp, price}) is appended to `bpi_data.json` by `Storage`.
3. After the configured number of samples, `GraphGenerator` produces `bpi_graph.png`.
4. `EmailSender` composes a short report that includes the maximum price over the run and attaches the PNG (if present), then sends via SMTP.
5. BusinessLogic actions are logged to stdout via `BusinessLogicLogger` to aid debugging.

## Troubleshooting

Common issues and solutions:

1. Missing graph file:
   - Graphs are only generated after a full collection run
   - Run a short test: `python bpi_collector.py --samples 5 --interval 2`

2. Email issues:
   - Verify SMTP settings in config.ini
   - Check network connectivity to SMTP server
   - For Gmail, ensure you're using an App Password with 2FA

3. Dependency issues:
   - Ensure all requirements are installed: `pip install -r requirements.txt`
   - Check virtual environment activation

4. Data formatting:
   - Timestamps are in UTC
   - For timezone adjustments, modify grapher.py or storage.py

## Developer Notes

- Logging: the BusinessLogic logger prints INFO and ERROR messages to stdout. Check these logs when debugging runs.
- Tests: there are no automated unit tests in the repository yet. To manually validate functionality, run the smoke test (`--test`) and a short collection (`--samples 5 --interval 2`) to exercise fetch, storage and graph generation.
- Adding unit tests and CI is a recommended next step.

## Security and housekeeping

- Never commit real credentials. Keep `config.ini` in `.gitignore` or use environment variables.

## License / Notes

This is a small utility intended for demonstration and light monitoring. Use responsibly and avoid excessive polling of public APIs.


## Docker Support

### Using Docker Compose (Recommended)

1. Start the services:
```bash
docker-compose up -d --build
```

This will start:
- `bpi_collector`: Data collection service
- `bpi_dashboard`: Web UI (http://localhost:8000)

2. View logs:
```bash
docker-compose logs -f
```

### Manual Docker Usage

1. Build the image:
```bash
docker build -t bpi-collector:latest .
```

2. Run the collector:
```bash
docker run --rm -v "$(pwd)/data:/app/data" \
    -e SMTP_SERVER=${SMTP_SERVER} \
    -e SMTP_PORT=${SMTP_PORT} \
    -e SMTP_USERNAME=${SMTP_USERNAME} \
    -e SMTP_PASSWORD=${SMTP_PASSWORD} \
    bpi-collector:latest
```

### Docker Tips
- Data is persisted in the host's `./data` directory
- Use environment variables or mounted `config.ini` for SMTP settings
- Dashboard updates automatically when new data is collected
- Use `./scripts/update_image.sh --compose` to rebuild and restart services


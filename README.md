
# BPI Collector

A Python utility that:
- Fetches cryptocurrency prices from Coinbase API (default: BTC-USD)
- Stores timestamped readings in JSON format
- Generates price trend graphs
- Sends email reports with maximum price and graph visualizations

The project supports multiple currency pairs and configurable sampling intervals.

## Key Components

- `bpi_collector.py` — Main CLI entrypoint
- `bpi_collector/` — Core modules:
  - `collector.py` — Main orchestrator
  - `fetcher.py` — API interaction
  - `storage.py` — Data persistence
  - `grapher.py` — Visualization
  - `emailer.py` — Email reporting
  - `config.py` — Configuration
  - `logger.py` — Logging system
- `dashboard.py` — Web interface
- `config.ini.sample` — Configuration template
- `docker-compose.yml` — Container orchestration

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

Email settings can be configured in two ways:

1. **Recommended:** Use `config.ini` file
   ```bash
   cp config.ini.sample config.ini
   ```
   Edit the `[smtp]` section with your email server details:
   - `server`, `port`, `username`, `password`, `from` (optional), `to` (recipients)

2. **Alternative:** Use environment variables
   - `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `EMAIL_FROM`, `EMAIL_TO`

**Note:** Gmail users should use an App Password when 2FA is enabled.

## How it works

1. Fetches cryptocurrency prices at specified intervals
2. Stores each data point (timestamp, price) to JSON
3. Generates price trend graph after collection completes
4. Sends email report with maximum price and attached graph
5. Logs all actions to stdout for monitoring

## Troubleshooting

Common issues:

1. **No graph generated**
   - Graphs only appear after a complete collection run
   - Try a short test: `python bpi_collector.py --samples 5 --interval 2`

2. **Email problems**
   - Check SMTP settings in config.ini
   - For Gmail, use an App Password with 2FA

3. **Missing dependencies**
   - Run `pip install -r requirements.txt`
   - Verify virtual environment is activated

4. **Time zone issues**
   - All timestamps are in UTC
   - To adjust, modify grapher.py or storage.py

## Developer Notes

- Logging outputs to stdout at INFO level
- Run smoke tests with `--test` flag or a short collection (`--samples 5 --interval 2`)
- Never commit real credentials - keep `config.ini` in `.gitignore` or use environment variables
- Future improvements:
  - Add unit tests
  - Implement CI/CD
  - Add rate limiting
  - Improve error handling

## License

This utility is for demonstration and light monitoring. Use responsibly and avoid excessive polling of public APIs.

## Docker Support

### Using Docker Compose (Recommended)

1. Start the services:
```bash
docker compose up -d --build
```

This will start:
- `bpi_collector`: Data collection service
- `bpi_dashboard`: Web UI (http://localhost:8000)

2. View logs:
```bash
docker compose logs -f
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
- Data persists in the host's `./data` directory
- Configure using environment variables or mounted `config.ini`
- Web dashboard automatically updates with new data
- Use `./scripts/update_image.sh --compose` to rebuild services


#!/usr/bin/env python3
#!/usr/bin/env python3
"""Thin CLI wrapper for the bpi_collector package."""

from __future__ import annotations

import argparse
import configparser
import os
from datetime import datetime
from bpi_collector.config import Config
from bpi_collector.logger import BusinessLogicLogger
from bpi_collector.collector import BPICollector
from bpi_collector.emailer import EmailSender
from bpi_collector.report_generator import ReportGenerator


def load_smtp_config_from_env():
    cfg = configparser.ConfigParser()
    config_path = os.path.join(os.getcwd(), 'config.ini')
    server = port = username = password = from_addr = to_addrs = None
    if os.path.exists(config_path):
        cfg.read(config_path)
        if 'smtp' in cfg:
            sec = cfg['smtp']
            server = sec.get('server')
            port = sec.getint('port', fallback=587)
            username = sec.get('username')
            password = sec.get('password')
            from_addr = sec.get('from', fallback=username)
            to_addrs = [x.strip() for x in sec.get('to', fallback=username).split(',') if x.strip()]

    server = server or os.getenv('SMTP_SERVER')
    port = port or int(os.getenv('SMTP_PORT', '587'))
    username = username or os.getenv('SMTP_USERNAME')
    password = password or os.getenv('SMTP_PASSWORD')
    from_addr = from_addr or os.getenv('EMAIL_FROM') or username
    env_to = os.getenv('EMAIL_TO')
    if not to_addrs:
        to_addrs = [x.strip() for x in (env_to or username or '').split(',') if x.strip()]

    return server, port, username, password, from_addr, to_addrs


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', action='store_true', help='Run a single fetch and exit')
    parser.add_argument('--send-test', action='store_true', help='Run a single fetch and attempt to send an email immediately (for SMTP troubleshooting)')
    parser.add_argument('--samples', type=int, default=60, help='Number of samples to collect')
    parser.add_argument('--interval', type=int, default=60, help='Interval seconds between samples')
    parser.add_argument('--pairs', type=str, help='Comma-separated currency pairs to sample (e.g. BTC-USD,ETH-USD)')
    args = parser.parse_args(argv)

    # For full collection runs we create a new per-run data file and graph
    if not args.test and not args.send_test:
        ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        data_dir = os.path.join(os.getcwd(), 'data')
        os.makedirs(data_dir, exist_ok=True)
        store_name = f"bpi_data_{ts}.json"
        graph_name = f"bpi_graph_{ts}.png"
        report_name = f"bpi_report_{ts}.pdf"
        cfg = Config(samples=args.samples, interval_seconds=args.interval,
                     store_path=os.path.join('data', store_name),
                     graph_path=os.path.join('data', graph_name))
        # Store report path for later use
        report_path = os.path.join('data', report_name)
    else:
        # keep defaults for quick tests
        cfg = Config(samples=args.samples, interval_seconds=args.interval)
    if args.pairs:
        cfg.currencies = [p.strip() for p in args.pairs.split(',') if p.strip()]
    logger = BusinessLogicLogger()
    collector = BPICollector(cfg, logger)

    if args.test:
        prices = collector.run_once()
        print("Fetched prices:")
        for p, v in prices.items():
            print(f"  {p}: ${v:.2f}")
        return 0

    if args.send_test:
        prices = collector.run_once()
        samples = collector.storage.read_all()
        # compute max across stored samples for the first pair (or any pair)
        if samples:
            first_sample_prices = samples[0].get('prices') or {}
            if first_sample_prices:
                first_pair = list(first_sample_prices.keys())[0]
            else:
                # fallback to configured currencies or BTC-USD
                first_pair = (cfg.currencies[0] if getattr(cfg, 'currencies', None) else 'BTC-USD')
            vals = [s.get('prices', {}).get(first_pair) for s in samples if s.get('prices') and s.get('prices').get(first_pair) is not None]
            max_price = max(vals, default=None)
        else:
            first_pair = next(iter(prices.keys()), 'BTC-USD')
            max_price = prices.get(first_pair)

        server, port, username, password, from_addr, to_addrs = load_smtp_config_from_env()
        if server and username and password and to_addrs:
            sender = EmailSender(server, port, username, password, logger)
            subject = f"BPI Test Report - Current {first_pair}: ${max_price:.2f}"
            
            # Send elegant email with HTML body and PDF attachment
            ok = sender.send_report_email(from_addr, to_addrs, subject, samples, 
                                        cfg.graph_path if os.path.exists(cfg.graph_path) else None)
            print("Email send succeeded" if ok else "Email send failed; check logs")
            return 0
        else:
            logger.error('SMTP not configured for send-test; set config.ini or env vars')
            return 1

    samples = collector.run_loop()
    if samples:
        # summarize max per first pair
        first_sample_prices = samples[0].get('prices') or {}
        if first_sample_prices:
            first_pair = list(first_sample_prices.keys())[0]
        else:
            first_pair = (cfg.currencies[0] if getattr(cfg, 'currencies', None) else 'BTC-USD')
        vals = [s.get('prices', {}).get(first_pair) for s in samples if s.get('prices') and s.get('prices').get(first_pair) is not None]
        max_price = max(vals, default=None)
        server, port, username, password, from_addr, to_addrs = load_smtp_config_from_env()
        if server and username and password and to_addrs:
            sender = EmailSender(server, port, username, password, logger)
            subject = f"BPI Report - Max {first_pair}: ${max_price:.2f}"
            
            try:
                # Send elegant email with HTML body and PDF attachment
                sender.send_report_email(from_addr, to_addrs, subject, samples, cfg.graph_path)
            except Exception as e:
                logger.error("Failed to generate report or send email", error=str(e))
        else:
            logger.info('SMTP not configured; skipping email')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
    

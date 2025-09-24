import os
import argparse
import configparser
from datetime import datetime
from bpi_collector.config import Config
from bpi_collector.logger import BusinessLogicLogger
from bpi_collector.collector import BPICollector
from bpi_collector.emailer import EmailSender
from bpi_collector.utils import get_price_statistics, validate_smtp_config


def load_smtp_config_from_env():
    cfg = configparser.ConfigParser()
    config_path = os.path.join(os.getcwd(), "config.ini")
    server = port = username = password = from_address = to_address = None

    if os.path.exists(config_path):
        cfg.read(config_path)
        if "smtp" in cfg:
            sec = cfg["smtp"]
            server = sec.get("server")
            port = sec.getint("port", fallback=587)
            username = sec.get("username")
            password = sec.get("password")
            from_address = sec.get("from", fallback=username)
            to_address = [
                x.strip()
                for x in sec.get("to", fallback=username).split(",")
                if x.strip()
            ]

    server = server or os.getenv("SMTP_SERVER")
    port = port or int(os.getenv("SMTP_PORT", "587"))
    username = username or os.getenv("SMTP_USERNAME")
    password = password or os.getenv("SMTP_PASSWORD")
    from_address = from_address or os.getenv("EMAIL_FROM") or username
    env_to = os.getenv("EMAIL_TO")

    if not to_address:
        to_address = [
            x.strip() for x in (env_to or username or "").split(",") if x.strip()
        ]

    return {
        "server": server,
        "port": port,
        "username": username,
        "password": password,
        "from": from_address,
        "to": to_address,
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--test", action="store_true", help="Run a single fetch and exit"
    )
    parser.add_argument(
        "--send-test",
        action="store_true",
        help="Run a single fetch and attempt to send an email immediately (for SMTP troubleshooting)",
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=int(os.getenv("SAMPLES", "60")),
        help="Number of samples to collect",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=int(os.getenv("INTERVAL", "60")),
        help="Interval seconds between samples",
    )
    parser.add_argument(
        "--pairs",
        type=str,
        help="Comma-separated currency pairs to sample (e.g. BTC-USD,ETH-USD)",
    )
    args = parser.parse_args(argv)

    if not args.test and not args.send_test:
        # Use timezone-aware UTC time with Z suffix
        from datetime import timezone

        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        data_dir = os.path.join(os.getcwd(), "data")
        os.makedirs(data_dir, exist_ok=True)
        store_name = f"bpi_data_{ts}.json"
        graph_name = f"bpi_graph_{ts}.png"
        cfg = Config(
            samples=args.samples,
            interval_seconds=args.interval,
            store_path=os.path.join("data", store_name),
            graph_path=os.path.join("data", graph_name),
        )

    else:
        cfg = Config(samples=args.samples, interval_seconds=args.interval)

    if args.pairs:
        cfg.currencies = [p.strip() for p in args.pairs.split(",") if p.strip()]

    logger = BusinessLogicLogger().logger
    collector = BPICollector(cfg, logger)

    if args.test:
        prices = collector.run_once()
        print("Fetched prices:")
        for p, v in prices.items():
            print(f"  {p}: ${v:.2f}")
        return 0
    smtp_config_env_values = load_smtp_config_from_env()

    if args.send_test:
        prices = collector.run_once()
        samples = collector.storage.read_all()

        if samples:
            first_pair, max_price = get_price_statistics(samples, cfg.currencies)
        else:
            first_pair = next(iter(prices.keys()), "BTC-USD")
            max_price = prices.get(first_pair)

        if validate_smtp_config(smtp_config_env_values):
            sender = EmailSender(
                smtp_server=smtp_config_env_values["server"],
                smtp_port=smtp_config_env_values["port"],
                username=smtp_config_env_values["username"],
                password=smtp_config_env_values["password"],
                logger=logger,
            )

            subject = f"BPI Test Report - Current {first_pair}: ${max_price:.2f}"

            ok = sender.send_report_email(
                subject=subject,
                samples=samples,
                to_address=smtp_config_env_values["to"],
                from_address=smtp_config_env_values["from"],
                graph_path=cfg.graph_path if os.path.exists(cfg.graph_path) else None,
            )
            print("Email send succeeded" if ok else "Email send failed; check logs")
            return 0

        else:
            logger.error(
                "SMTP not configured for send-test; set config.ini or env vars"
            )
            return 1

    samples = collector.run_loop()
    if samples:
        first_pair, max_price = get_price_statistics(samples, cfg.currencies)

        if validate_smtp_config(smtp_config_env_values):
            sender = EmailSender(
                smtp_server=smtp_config_env_values["server"],
                smtp_port=smtp_config_env_values["port"],
                username=smtp_config_env_values["username"],
                password=smtp_config_env_values["password"],
                logger=logger,
            )
            subject = f"BPI Report - Max {first_pair}: ${max_price:.2f}"

            try:
                sender.send_report_email(
                    smtp_config_env_values["from"],
                    smtp_config_env_values["to"],
                    subject,
                    samples,
                    cfg.graph_path,
                )

            except Exception as e:
                logger.error("Failed to generate report or send email", error=str(e))
        else:
            logger.info("SMTP not configured; skipping email")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

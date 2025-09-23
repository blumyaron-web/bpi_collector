from flask import Flask, render_template, send_file, jsonify
import os
import glob
import json

app = Flask(__name__, static_folder="static", template_folder="templates")

DATA_DIR = os.path.join(os.getcwd(), "data")


def latest_run_files():
    files = glob.glob(os.path.join(DATA_DIR, "bpi_data_*.json"))
    if not files:
        return None, None
    files.sort()
    latest_json = files[-1]
    ts = os.path.splitext(os.path.basename(latest_json))[0].replace("bpi_data_", "")
    graph = os.path.join(DATA_DIR, f"bpi_graph_{ts}.png")
    return latest_json, graph


def get_collection_progress():
    latest_json, _ = latest_run_files()
    if not latest_json:
        return {"in_progress": False, "samples_collected": 0, "total_samples": 0}

    with open(latest_json, "r", encoding="utf-8") as f:
        data = json.load(f)
        samples_collected = len(data)

    # First try environment variables
    total_samples = int(os.getenv("SAMPLES", "0"))

    # If not in env, try config file
    if total_samples == 0:
        config_path = os.path.join(os.getcwd(), "config.ini")
        if os.path.exists(config_path):
            import configparser

            config = configparser.ConfigParser()
            config.read(config_path)
            total_samples = int(config.get("collection", "samples", fallback=60))
        else:
            total_samples = 60

    return {
        "in_progress": samples_collected < total_samples,
        "samples_collected": samples_collected,
        "total_samples": total_samples,
    }


@app.route("/")
def index():
    latest_json, graph = latest_run_files()
    return render_template("index.html", has_run=bool(latest_json))


@app.route("/latest/data")
def latest_data():
    latest_json, _ = latest_run_files()
    if not latest_json:
        return jsonify([])
    with open(latest_json, "r", encoding="utf-8") as f:
        return jsonify(json.load(f))


@app.route("/latest/graph")
def latest_graph():
    _, graph = latest_run_files()
    if not graph or not os.path.exists(graph):
        return ("", 404)
    return send_file(graph, mimetype="image/png")


@app.route("/progress")
def collection_progress():
    return jsonify(get_collection_progress())


@app.route("/email_status")
def email_status():
    status_file = os.path.join(DATA_DIR, "email_status.json")
    if os.path.exists(status_file):
        try:
            with open(status_file, "r") as f:
                data = json.load(f)

                # Format timestamps to local time for display
                def format_timestamp(ts):
                    if not ts:
                        return None
                    try:
                        from datetime import datetime, timezone, timedelta

                        if isinstance(ts, str):
                            if ts.endswith("Z"):
                                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                            else:
                                dt = datetime.fromisoformat(ts)
                        else:
                            dt = ts

                        # Ensure the datetime is timezone-aware
                        if dt.tzinfo is None:
                            dt = dt.replace(tzinfo=timezone.utc)

                        # Convert to Jerusalem timezone (UTC+3)
                        jerusalem_tz = timezone(timedelta(hours=3))
                        local_dt = dt.astimezone(jerusalem_tz)

                        return (
                            local_dt.strftime("%Y-%m-%d %I:%M:%S %p") + " (Jerusalem)"
                        )
                    except Exception:
                        return ts

                # Helper to process each status entry
                def process_entry(entry):
                    if not isinstance(entry, dict):
                        return entry

                    # If already has formatted_time, use it
                    if "formatted_time" in entry:
                        return entry

                    # Format timestamp if available
                    if "timestamp" in entry:
                        entry["formatted_time"] = format_timestamp(entry["timestamp"])
                    elif "last_send" in entry:
                        entry["formatted_time"] = format_timestamp(entry["last_send"])

                    return entry

                # Handle both old and new format
                if isinstance(data, dict):
                    # Old format with single status
                    processed_data = process_entry(data)
                    return jsonify(
                        {"latest": processed_data, "history": [processed_data]}
                    )
                else:
                    # New format with history array
                    processed_data = [process_entry(entry) for entry in data]
                    return jsonify(
                        {
                            "latest": (
                                processed_data[0]
                                if processed_data
                                else {
                                    "timestamp": None,
                                    "success": False,
                                    "subject": None,
                                }
                            ),
                            "history": processed_data,
                        }
                    )
        except Exception as e:
            app.logger.error(f"Error reading email status: {e}")

    # Default response if file doesn't exist or error occurs
    empty_status = {"timestamp": None, "success": False, "subject": None}
    return jsonify({"latest": empty_status, "history": []})


if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    app.run(host="0.0.0.0", port=8000, debug=False)

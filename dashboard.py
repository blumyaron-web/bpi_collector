from flask import Flask, render_template, send_file, jsonify
import os
import glob
import json

app = Flask(__name__, static_folder='static', template_folder='templates')

DATA_DIR = os.path.join(os.getcwd(), 'data')


def latest_run_files():
    files = glob.glob(os.path.join(DATA_DIR, 'bpi_data_*.json'))
    if not files:
        return None, None
    files.sort()
    latest_json = files[-1]
    ts = os.path.splitext(os.path.basename(latest_json))[0].replace('bpi_data_', '')
    graph = os.path.join(DATA_DIR, f'bpi_graph_{ts}.png')
    return latest_json, graph

def get_collection_progress():
    latest_json, _ = latest_run_files()
    if not latest_json:
        return {"in_progress": False, "samples_collected": 0, "total_samples": 0}
    
    with open(latest_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
        # Get the number of samples collected
        samples_collected = len(data)
        
    # Read config to get total samples
    config_path = os.path.join(os.getcwd(), 'config.ini')
    if os.path.exists(config_path):
        import configparser
        config = configparser.ConfigParser()
        config.read(config_path)
        total_samples = int(config.get('collection', 'samples', fallback=60))
    else:
        total_samples = 60  # default value
        
    return {
        "in_progress": samples_collected < total_samples,
        "samples_collected": samples_collected,
        "total_samples": total_samples
    }


@app.route('/')
def index():
    latest_json, graph = latest_run_files()
    return render_template('index.html', has_run=bool(latest_json))


@app.route('/latest/data')
def latest_data():
    latest_json, _ = latest_run_files()
    if not latest_json:
        return jsonify([])
    with open(latest_json, 'r', encoding='utf-8') as f:
        return jsonify(json.load(f))


@app.route('/latest/graph')
def latest_graph():
    _, graph = latest_run_files()
    if not graph or not os.path.exists(graph):
        return ('', 404)
    return send_file(graph, mimetype='image/png')

@app.route('/progress')
def collection_progress():
    return jsonify(get_collection_progress())

if __name__ == '__main__':
    os.makedirs(DATA_DIR, exist_ok=True)
    app.run(host='0.0.0.0', port=8000, debug=False)

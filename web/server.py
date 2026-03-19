"""
RGVL Web Dashboard - Flask Server
"""
import os
from flask import Flask, send_from_directory, jsonify

app = Flask(__name__, static_folder='.')


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory('.', 'favicon.ico')


@app.route('/favicon.png')
def favicon_png():
    return send_from_directory('.', 'favicon.png')


@app.route('/api/proxy/<path:endpoint>')
def proxy(endpoint):
    """Proxy requests to RGVL Data API (now on 5004)"""
    import requests
    try:
        resp = requests.get(f'http://localhost:5004/api/{endpoint}', timeout=10)
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({'error': str(e)})


def handler(event, context):
    return app(event, context)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5002)

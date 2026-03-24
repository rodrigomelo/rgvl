"""
RGVL Web Dashboard - Flask Server
"""
import os
from flask import Flask, send_from_directory, jsonify

app = Flask(__name__, static_folder='.')


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/auth.js')
def auth_js():
    return send_from_directory('.', 'auth.js')


@app.route('/callback.html')
def callback_html():
    return send_from_directory('.', 'callback.html')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory('.', 'favicon.ico')


@app.route('/favicon.png')
def favicon_png():
    return send_from_directory('.', 'favicon.png')


@app.route('/api/proxy/<path:endpoint>')
def proxy(endpoint):
    """Proxy requests to RGVL Data API."""
    import requests
    api_url = os.environ.get('API_URL', 'http://localhost:5003')
    try:
        resp = requests.get(f'{api_url}/api/{endpoint}', timeout=10)
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({'error': str(e)})


def handler(event, context):
    return app(event, context)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    app.run(host='0.0.0.0', port=port)

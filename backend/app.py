from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from downloader import handle_download

app = Flask(__name__, static_folder="../frontend/dist", static_url_path="/")
CORS(app)

@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.route("/health")
def health():
    return {"status": "ok"}

@app.route("/download", methods=["POST"])
def download():
    data = request.json
    result = handle_download(data)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

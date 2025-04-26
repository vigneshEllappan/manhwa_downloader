from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import os
import base64
from downloader import handleDownload, handleChaptersGeneration, loadExistingCache
from pathlib import Path
import logging

# Configure the logging system
logging.basicConfig(
    level=logging.INFO,  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),  # Log to console
    ]
)

logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder="../frontend/build", static_url_path="/")
CORS(app)

if os.getenv('FLASK_ENV') == 'development':
    app.debug = True
else:
    app.debug = False

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

@app.route("/api/health")
def health():
    return {"status": "ok"}

@app.route("/api/download", methods=["POST"])
def download():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing JSON body"}), 400

        file_path = handleDownload(data)

        if not file_path or not Path(file_path).exists():
            loadExistingCache()
            return jsonify({"error": "File not found in cache/ Error Downloading"}), 404

        return send_file(
            file_path,
            as_attachment=True,
            download_name=f"{data['chapter']}.cbz",
            mimetype="application/octet-stream"
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/chapters", methods=["GET"])
def getChaptersList():
    title = request.args.get('title')
    result = handleChaptersGeneration(title)
    if not result:
        return jsonify({"error":"Error With Chapters Generation"}), 500
    return jsonify(result)


if __name__ == "__main__":
    loadExistingCache()
    app.run(host='0.0.0.0', port=8080)
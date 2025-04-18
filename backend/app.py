from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from downloader import handleDownload, handleChaptersGeneration

app = Flask(__name__, static_folder="../frontend/build", static_url_path="/")
CORS(app)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

@app.route("/health")
def health():
    return {"status": "ok"}

@app.route("/download", methods=["POST"])
def download():
    data = request.json
    result = handleDownload(data)
    return jsonify(result)

@app.route("/chapters", methods=["GET"])
def getChaptersList():
    title = request.args.get('title')
    result = handleChaptersGeneration(title)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)

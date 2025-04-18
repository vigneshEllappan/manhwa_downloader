from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import base64
from downloader import handleDownload, handleChaptersGeneration

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

@app.route("/health")
def health():
    return {"status": "ok"}

@app.route("/download", methods=["POST"])
def download():
    try:
        # Generate the CBZ in memory
        data = request.json
        result = handleDownload(data)

        # Encode the CBZ content as base64
        encoded_file = base64.b64encode(result).decode("utf-8")

        # Send the base64-encoded file inside the JSON response along with statusCode
        response_data = {
            "statusCode": 200,
            "file": encoded_file
        }
        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({"statusCode": 500, "error": str(e)}), 500


@app.route("/chapters", methods=["GET"])
def getChaptersList():
    title = request.args.get('title')
    result = handleChaptersGeneration(title)
    return jsonify(result)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)

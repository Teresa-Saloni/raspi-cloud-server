import os
from flask import Flask, request, jsonify

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 🔹 Root route
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Raspberry Pi Cloud Server is running 🚀",
        "upload_endpoint": "/upload",
        "train_endpoint": "/train"
    })

# 🔹 Upload endpoint
@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files["file"]
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    return jsonify({"status": "success", "filename": file.filename})

# 🔹 Dummy training endpoint
@app.route("/train", methods=["POST"])
def train_model():
    return jsonify({"status": "success", "message": "Training started on uploaded data 🚀"})

if __name__ == "__main__":
    # ✅ Important fix for Render: use provided PORT + 0.0.0.0
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

# ---------------------------------
# Flask setup
# ---------------------------------
app = Flask(__name__)
CORS(app)

# ---------------------------------
# Environment variables
# ---------------------------------
API_KEY = os.environ.get("GOOGLE_API_KEY")

if not API_KEY:
    raise ValueError("GOOGLE_API_KEY is not defined")

MY_NAME = "Salvador"

# ✅ Force Gemini stable API v1
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1/"
    "models/gemini-1.5-flash:generateContent"
)

# ---------------------------------
# Helper: Safe text extraction
# ---------------------------------
def extract_text(result):
    try:
        candidates = result.get("candidates", [])

        for candidate in candidates:
            content = candidate.get("content", {})
            parts = content.get("parts", [])

            for part in parts:
                text = part.get("text")
                if text:
                    return text.strip()

        return "AI could not generate a response."

    except Exception:
        return "Error parsing AI response."


# ---------------------------------
# Health check route
# ---------------------------------
@app.route("/")
def home():
    return "API running ✅"


# ---------------------------------
# Generate review endpoint
# ---------------------------------
@app.route("/generate_review", methods=["POST"])
def generate_review():
    try:
        data = request.json

        if not data:
            return jsonify({"review": "No data received"}), 400

        speed = data.get("speed", 5)
        service = data.get("service", 5)
        extra = data.get("extra", "")

        prompt = (
            f"Write a short customer-style feedback comment about a car rental experience."
            f"Mention that {MY_NAME} provided excellent outdoor service. "
            f"Speed rating: {speed}/5. Service rating: {service}/5. "
            f"Additional info: {extra}. "
            f"Do not use emojis. Do not use quotation marks."
        )

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }

        response = requests.post(
            f"{GEMINI_URL}?key={API_KEY}",
            json=payload,
            timeout=30
        )

        result = response.json()

        review = extract_text(result)

        return jsonify({
            "review": review.replace('"', '')
        })

    except Exception as e:
        print("DEBUG ERROR:", str(e))
        return jsonify({"review": f"Server error: {str(e)}"}), 500


# ---------------------------------
# Run locally
# ---------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

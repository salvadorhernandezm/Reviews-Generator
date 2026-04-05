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
    print("⚠️ GOOGLE_API_KEY missing")

MY_NAME = "Salvador"

# ✅ UPDATED MODEL
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1/"
    "models/gemini-1.5-flash-latest:generateContent"
)

# ---------------------------------
# Extract text safely
# ---------------------------------
def extract_text(result):

    candidates = result.get("candidates")

    if not candidates:
        print("DEBUG: No candidates returned")
        return "AI could not generate a response."

    try:
        return candidates[0]["content"]["parts"][0]["text"].strip()
    except Exception:
        return "Error parsing AI response."


# ---------------------------------
# Health check
# ---------------------------------
@app.route("/")
def home():
    return "API running ✅"


# ---------------------------------
# Generate Review
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
            f"Write a short Google review about a car rental experience. "
            f"Mention that {MY_NAME} provided excellent outdoor service. "
            f"Speed rating {speed}/5, service rating {service}/5. "
            f"{extra}. No emojis. No quotation marks."
        )

        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ]
        }

        print("Calling Gemini API...")

        response = requests.post(
            f"{GEMINI_URL}?key={API_KEY}",
            json=payload,
            timeout=30
        )

        print("STATUS:", response.status_code)

        result = response.json()
        print("RAW GEMINI RESPONSE:", result)

        review = extract_text(result)

        return jsonify({"review": review.replace('"', '')})

    except Exception as e:
        print("DEBUG ERROR:", str(e))
        return jsonify({"review": f"Server error: {str(e)}"}), 500


# ---------------------------------
# Run locally
# ---------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

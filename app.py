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
    print("⚠️ WARNING: GOOGLE_API_KEY is not defined")

MY_NAME = "Salvador"

# ✅ Gemini Stable API (NO SDK — direct HTTP call)
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1/"
    "models/gemini-1.5-flash-latest:generateContent"
)

# ---------------------------------
# Helper: Extract text safely
# ---------------------------------
def extract_text(result):
    try:
        candidates = result.get("candidates", [])

        if not candidates:
            print("DEBUG: No candidates returned")
            return "AI could not generate a response."

        for candidate in candidates:
            content = candidate.get("content", {})
            parts = content.get("parts", [])

            for part in parts:
                text = part.get("text")
                if text:
                    return text.strip()

        return "AI returned empty content."

    except Exception as e:
        print("DEBUG PARSE ERROR:", str(e))
        return "Error parsing AI response."


# ---------------------------------
# Health Check Route
# ---------------------------------
@app.route("/")
def home():
    return "API running ✅"


# ---------------------------------
# Generate Review Endpoint
# ---------------------------------
@app.route("/generate_review", methods=["POST"])
def generate_review():

    if not API_KEY:
        return jsonify({"review": "Server missing API key"}), 500

    try:
        data = request.json

        if not data:
            return jsonify({"review": "No data received"}), 400

        speed = data.get("speed", 5)
        service = data.get("service", 5)
        extra = data.get("extra", "")

        # ✅ Stronger prompt = better responses
        prompt = f"""
Write a natural customer Google review about a car rental experience.

Requirements:
- Mention that {MY_NAME} provided excellent outdoor service.
- Sound human and realistic.
- 2 sentences maximum.
- No emojis.
- No quotation marks.

Ratings:
Speed: {speed}/5
Service: {service}/5

Extra customer comments:
{extra}
"""

        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.8,
                "maxOutputTokens": 120
            }
        }

        response = requests.post(
            f"{GEMINI_URL}?key={API_KEY}",
            json=payload,
            timeout=30
        )

        # DEBUG
        print("STATUS:", response.status_code)

        result = response.json()

        print("RAW GEMINI RESPONSE:", result)

        review = extract_text(result)

        return jsonify({
            "review": review.replace('"', '')
        })

    except Exception as e:
        print("DEBUG ERROR:", str(e))
        return jsonify({"review": f"Server error: {str(e)}"}), 500


# ---------------------------------
# Local Run
# ---------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

API_KEY = os.environ.get("GOOGLE_API_KEY")

MY_NAME = "Salvador"

# ✅ WORKING MODEL (2026)
GEMINI_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"

def extract_text(result):
    try:
        return result["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception:
        print("DEBUG:", result)
        return "AI could not generate a response."

@app.route("/")
def home():
    return "API running ✅"

@app.route("/generate_review", methods=["POST"])
def generate_review():
    try:
        data = request.json or {}

        speed = data.get("speed", 5)
        service = data.get("service", 5)
        extra = data.get("extra", "")

        prompt = (
            f"Write a short Google review about a car rental experience. "
            f"Mention that {MY_NAME} provided excellent outdoor service. "
            f"Speed {speed}/5. Service {service}/5. {extra}. "
            f"No emojis. No quotation marks."
        )

        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ]
        }

        response = requests.post(
            f"{GEMINI_URL}?key={API_KEY}",
            json=payload,
            timeout=30,
        )

        print("STATUS:", response.status_code)

        result = response.json()
        print("RAW GEMINI RESPONSE:", result)

        review = extract_text(result)

        return jsonify({"review": review.replace('"', '')})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"review": "Server error"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

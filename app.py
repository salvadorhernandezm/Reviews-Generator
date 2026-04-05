import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

API_KEY = os.environ.get("GOOGLE_API_KEY")

if not API_KEY:
    raise ValueError("GOOGLE_API_KEY no definida")

MY_NAME = "Salvador"

# ✅ Endpoint v1 FORZADO
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1/"
    "models/gemini-1.5-flash:generateContent"
)


@app.route("/")
def home():
    return "API running ✅"


@app.route("/generate_review", methods=["POST"])
def generate_review():
    try:
        data = request.json

        speed = data.get("speed", 5)
        service = data.get("service", 5)
        extra = data.get("extra", "")

        prompt = (
            f"Write a 2-sentence Google review for Hertz. "
            f"Mention that {MY_NAME} provided excellent outdoor service. "
            f"Speed: {speed}/5. Service: {service}/5. "
            f"Additional info: {extra}. "
            f"No emojis. No quotation marks."
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

        review = result["candidates"][0]["content"]["parts"][0]["text"]

        return jsonify({"review": review.strip().replace('"', '')})

    except Exception as e:
        print("DEBUG ERROR:", str(e))
        return jsonify({"review": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

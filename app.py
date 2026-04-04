import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS

print("GENAI VERSION:", genai.__version__)

app = Flask(__name__)
CORS(app)

# -----------------------
# API KEY
# -----------------------
API_KEY = os.environ.get("GOOGLE_API_KEY")

if not API_KEY:
    raise ValueError("GOOGLE_API_KEY no definida")

genai.configure(api_key=API_KEY)

# ⚠️ CREAR MODELO UNA SOLA VEZ (IMPORTANTE)
model = genai.GenerativeModel(
    model_name="models/gemini-1.5-flash"
)

MY_NAME = "Salvador"


@app.route("/")
def home():
    return "API running ✅"


@app.route("/generate_review", methods=["POST"])
def generate_review():
    try:
        data = request.json

        if not data:
            return jsonify({"review": "No se recibieron datos"}), 400

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

        response = model.generate_content(prompt)

        return jsonify({
            "review": response.text.strip().replace('"', '')
        })

    except Exception as e:
        print("DEBUG ERROR:", str(e))
        return jsonify({"review": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

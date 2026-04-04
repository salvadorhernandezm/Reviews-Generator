import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai

# -----------------------------
# Flask setup
# -----------------------------
app = Flask(__name__)
CORS(app)

# -----------------------------
# API KEY
# -----------------------------
API_KEY = os.environ.get("GOOGLE_API_KEY")

if not API_KEY:
    raise ValueError("GOOGLE_API_KEY no está definida")

# Cliente Gemini (API v1 real)
client = genai.Client(api_key=API_KEY)

# Nombre del empleado
MY_NAME = "Salvador"


# -----------------------------
# Health check route
# -----------------------------
@app.route("/")
def home():
    return "API running ✅"


# -----------------------------
# Generate Review Endpoint
# -----------------------------
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

        # 🔥 Llamada correcta API v1
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
        )

        review_text = response.text.strip().replace('"', "")

        return jsonify({"review": review_text})

    except Exception as e:
        print(f"DEBUG ERROR: {str(e)}")
        return jsonify({"review": f"Error del Servidor: {str(e)}"}), 500


# -----------------------------
# Run local
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

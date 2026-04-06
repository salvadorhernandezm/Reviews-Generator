import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Esto permite que tu web en Netlify se comunique con Render sin bloqueos
CORS(app)

# Configuración de la API (Asegúrate de tener la variable GOOGLE_API_KEY en Render)
API_KEY = os.environ.get("AIzaSyAc4LDaQjTDt6tIUhEppT1pwPcehEaXRqU")

# Esta es la URL exacta que tu cuenta SÍ reconoce:
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-001:generateContent"

@app.route("/", methods=["GET"])
def home():
    return "API de Reseñas de Salvador: ONLINE ✅"

@app.route("/generate_review", methods=["POST"])
def generate_review():
    try:
        # 1. Recibir datos del frontend
        data = request.json or {}
        speed = data.get("speed", 5)
        service = data.get("service", 5)
        extra = data.get("extra", "")

        # 2. Construir el mensaje para la IA
        prompt = (
            f"Escribe una reseña corta para Google sobre Hertz. "
            f"Menciona que Salvador dio un excelente servicio afuera (outdoor service). "
            f"Puntaje de rapidez: {speed}/5, Puntaje de servicio: {service}/5. "
            f"Comentario adicional: {extra}. "
            f"Respuesta en español, sin emojis y sin comillas."
        )

        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }

        print(f"--- 🛰️ ENVIANDO PETICIÓN A GOOGLE ---")

        # 3. Llamada a Google Gemini
        response = requests.post(
            f"{GEMINI_URL}?key={API_KEY}",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )

        # 4. LOGS DE RASTREO (Esto verás en Render)
        print(f"--- 📡 STATUS CODE GOOGLE: {response.status_code} ---")
        
        if response.status_code != 200:
            error_msg = response.text
            print(f"--- ❌ ERROR DE GOOGLE: {error_msg} ---")
            return jsonify({"review": f"Error de Google: {response.status_code}"}), response.status_code

        # 5. Extraer la reseña
        result = response.json()
        review_text = result["candidates"][0]["content"]["parts"][0]["text"].strip()

        # 🔥 LA PRUEBA REINA: Imprime la reseña en la consola de Render
        print(f"--- ✅ RESEÑA GENERADA: ---")
        print(review_text)
        print(f"---------------------------")

        return jsonify({"review": review_text})

    except Exception as e:
        print(f"--- 🚨 ERROR CRÍTICO: {str(e)} ---")
        return jsonify({"review": f"Error del servidor: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

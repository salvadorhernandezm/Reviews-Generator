import os
import requests
import random
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Permitir que Netlify se comunique con Render
CORS(app)

# Configuración de la API desde variables de entorno de Render
API_KEY = os.environ.get("GOOGLE_API_KEY")

# URL del modelo Gemini 2.5 Flash (Versión actualizada 2026)
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

@app.route("/", methods=["GET"])
def home():
    return "Hertz Review Generator - Salvador Edition ✅"

@app.route("/generate_review", methods=["POST"])
def generate_review():
    try:
        # 1. Recibir datos del frontend (Netlify)
        data = request.json or {}
        speed = int(data.get("speed", 5))
        service = int(data.get("service", 5))
        extra = data.get("extra", "")

        # 2. Lógica de Variedad para que no suenen igual
        estilos = [
            "concise and direct", 
            "friendly and casual", 
            "professional and brief", 
            "enthusiastic",
            "simple and honest"
        ]
        estilo_random = random.choice(estilos)

        # 3. Ajustar el tono según el puntaje (Lógica para negativas/positivas)
        if service <= 2 or speed <= 2:
            mood = "disappointed and honest about the wait or service"
            instruction = "Be constructive but mention the delay or issue."
        elif service == 3 or speed == 3:
            mood = "neutral and fair"
            instruction = "Mention it was okay but nothing special."
        else:
            mood = f"very satisfied in a {estilo_random} way"
            instruction = "Highlight Salvador's excellent outdoor service."

        # 4. Construcción del Prompt Dinámico
        prompt = (
            f"Write a unique, 1-sentence Google review for Hertz in French. "
            f"Context: Salvador helped me with the outdoor service. "
            f"Speed rating: {speed}/5. Service rating: {service}/5. "
            f"Additional customer comment: '{extra}'. "
            f"Tone: {mood}. {instruction} "
            f"CRITICAL: Change the sentence structure, do not start all reviews the same way. "
            f"Only English. No emojis. No quotes. No star scores in the text."
        )

        # 5. Preparar el paquete (Payload) para Google
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }

        print(f"--- 🛰️ ENVIANDO PETICIÓN A GOOGLE (Modelo 2.5) ---")

        # 6. Llamada a la API de Google
        response = requests.post(
            f"{GEMINI_URL}?key={API_KEY}",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )

        # 7. Verificación de Respuesta
        print(f"--- 📡 STATUS CODE GOOGLE: {response.status_code} ---")
        
        if response.status_code != 200:
            error_data = response.text
            print(f"--- ❌ ERROR DE GOOGLE: {error_data} ---")
            return jsonify({"review": "Error generating review. Check logs."}), response.status_code

        # 8. Extraer y limpiar el texto generado
        result = response.json()
        review_text = result["candidates"][0]["content"]["parts"][0]["text"].strip()

        print(f"--- ✅ RESEÑA GENERADA: {review_text} ---")

        return jsonify({"review": review_text})

    except Exception as e:
        print(f"--- 🚨 ERROR CRÍTICO: {str(e)} ---")
        return jsonify({"review": f"Server error: {str(e)}"}), 500

if __name__ == "__main__":
    # Render usa el puerto 10000 por defecto
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

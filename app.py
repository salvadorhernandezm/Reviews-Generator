import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS

# Forzamos la versión estable antes de cualquier otra cosa
os.environ["GOOGLE_GENERATIVE_AI_API_VERSION"] = "v1"

app = Flask(__name__)
CORS(app)

# Configuración de la API
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

# Usamos gemini-1.5-flash que es el más compatible hoy en día
model = genai.GenerativeModel('gemini-1.5-flash')

MY_NAME = "Salvador"

@app.route('/generate_review', methods=['POST'])
def generate_review():
    try:
        data = request.json
        if not data:
            return jsonify({"review": "No data received"}), 400

        speed = data.get('speed', 5)
        service = data.get('service', 5)
        quality = data.get('quality', 5)
        extra = data.get('extra', "")

        # Prompt en una sola línea para evitar errores de comillas triples
        prompt = f"Escribe una reseña de Google para Hertz en inglés. El empleado {MY_NAME} ayudó con dudas del coche o bluetooth. Rapidez: {speed}/5, Servicio: {service}/5. Nota del cliente: {extra}. REGLAS: Menciona a {MY_NAME}, sin emojis, máximo 2 frases, muy positivo."

        response = model.generate_content(prompt)
        
        if response and response.text:
            return jsonify({"review": response.text.strip().replace('"', '')})
        else:
            return jsonify({"review": "Error: IA sin respuesta"}), 500

    except Exception as e:
        print(f"CRASH ERROR: {str(e)}")
        return jsonify({"review": f"Backend Error: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS

# 1. FORZADO TOTAL DE VERSIÓN (Antes de configurar nada)
os.environ["GOOGLE_GENERATIVE_AI_API_VERSION"] = "v1"

app = Flask(__name__)
CORS(app)

# 2. CONFIGURACIÓN
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

# 3. EL MODELO (Usamos Pro para máxima estabilidad)
model = genai.GenerativeModel('gemini-pro')

MY_NAME = "Salvador"

@app.route('/generate_review', methods=['POST'])
def generate_review():
    try:
        data = request.json
        speed = data.get('speed', 5)
        service = data.get('service', 5)
        extra = data.get('extra', "")

        # Prompt simple en una línea para evitar errores de comillas
        prompt = f"Write a professional 5-star review for Hertz. {MY_NAME} assisted me with the car and tech. Speed: {speed}/5, Service: {service}/5. Note: {extra}. Rules: Mention {MY_NAME}, no emojis, 2 sentences max."

        response = model.generate_content(prompt)
        
        if response and response.text:
            return jsonify({"review": response.text.strip().replace('"', '')})
        else:
            return jsonify({"review": "Error: IA vacía"}), 500

    except Exception as e:
        print(f"CRASH ERROR: {str(e)}")
        return jsonify({"review": f"Backend Error: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

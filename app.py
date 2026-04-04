import os
import google.generativeai as genai
print("GENAI VERSION:", genai.__version__)
from flask import Flask, request, jsonify
from flask_cors import CORS

# ESTA LÍNEA ES EL ANTÍDOTO: Fuerza a la librería a ignorar v1beta
os.environ["GOOGLE_GENERATIVE_AI_API_VERSION"] = "v1"

app = Flask(__name__)
CORS(app)

# Configuración de API
API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

# Nombre del empleado
MY_NAME = "Salvador"

@app.route('/generate_review', methods=['POST'])
def generate_review():
    try:
        data = request.json
        if not data:
            return jsonify({"review": "No se recibieron datos"}), 400

        # Extraemos las variables del frontend
        speed = data.get('speed', 5)
        service = data.get('service', 5)
        extra = data.get('extra', "")

        # Usamos el modelo flash-001 que es el más estable en despliegues cloud
        model = genai.GenerativeModel('gemini-1.5-flash')

        # Prompt simplificado en una sola línea para evitar errores de comillas triples
        prompt = f"Write a 2-sentence Google review for Hertz. Mention that {MY_NAME} provided excellent outdoor service. Speed: {speed}/5, Service: {service}/5. Additional info: {extra}. No emojis, no quotes."

        # Llamada a la IA
        response = model.generate_content(prompt)
        
        if response and response.text:
            return jsonify({"review": response.text.strip().replace('"', '')})
        else:
            return jsonify({"review": "La IA no pudo generar el texto"}), 500

    except Exception as e:
        # Esto imprimirá el error real en los logs de Render
        print(f"DEBUG ERROR: {str(e)}")
        return jsonify({"review": f"Error del Servidor: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS

# Force stable API version
os.environ["GOOGLE_GENERATIVE_AI_API_VERSION"] = "v1"

app = Flask(__name__)
CORS(app)

# 1. Setup API Key
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

# 2. Setup Model (1.5-flash is the current standard)
model = genai.GenerativeModel('gemini-1.5-flash')

MY_NAME = "Salvador"

@app.route('/generate_review', methods=['POST'])
def generate_review():
    try:
        data = request.json
        if not data:
            return jsonify({"review": "No data received"}), 400

        # Extract values
        speed = data.get('speed', 5)
        service = data.get('service', 5)
        extra = data.get('extra', "")

        # Single-line prompt to avoid triple-quote syntax errors
        prompt = f"Write a 5-star Google review for Hertz. {MY_NAME} helped with the car lot/tech. Speed: {speed}/5, Service: {service}/5. Note: {extra}. Rules: Mention {MY_NAME}, no emojis, max 2 sentences, be very positive."

        response = model.generate_content(prompt)
        
        if response and response.text:
            clean_review = response.text.strip().replace('"', '')
            return jsonify({"review": clean_review})
        else:
            return jsonify({"review": "AI Error: Empty response"}), 500

    except Exception as e:
        print(f"CRASH ERROR: {str(e)}")
        return jsonify({"review": f"Backend Error: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

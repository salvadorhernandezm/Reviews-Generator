import os

# CRITICAL FIX: This environment variable MUST be set BEFORE importing the AI library
os.environ["GOOGLE_GENERATIVE_AI_API_VERSION"] = "v1"

import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 1. Setup API Key (Make sure this is in your Render Environment Variables!)
api_key = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# 2. Setup Model (Using the full 'models/' path to avoid 404 errors)
model = genai.GenerativeModel('models/gemini-pro')

MY_NAME = "Salvador"

@app.route('/generate_review', methods=['POST'])
def generate_review():
    try:
        # Get data from Netlify
        data = request.json
        if not data:
            return jsonify({"review": "Error: No data received"}), 400

        speed = data.get('speed', 5)
        service = data.get('service', 5)
        quality = data.get('quality', 5)
        extra = data.get('extra', "")

        # Personalized Prompt
        prompt = f"""
        Write a short Google Maps review for Hertz. 
        The customer was assisted outside at the car lot by {MY_NAME}.

        CONTEXT:
        - {MY_NAME} helped with: car issues, Bluetooth/CarPlay, or general questions.
        - Ratings (1-5): Speed {speed}, Service {service}, Quality {quality}.
        - Customer note: "{extra}"

        STRICT RULES:
        1. MENTION {MY_NAME} by name.
        2. NO EMOJIS.
        3. BRAND ADVOCACY: Stay positive towards Hertz.
        4. REALISM: Max 2 sentences. Natural English.
        5. NO NUMBERS: Don't mention '5/5' or 'stars' in the text.
        """

        # Generate the content
        response = model.generate_content(prompt)
        
        # Safety check for the response
        if not response or not response.text:
            return jsonify({"review": "AI was unable to generate text. Please try again."}), 500

        clean_review = response.text.strip().replace('"', '')

        return jsonify({"review": clean_review})

    except Exception as e:
        # This logs the error to your Render dashboard
        print(f"CRASH ERROR: {str(e)}")
        return jsonify({"review": f"AI Error: {str(e)}"}), 500

if __name__ == '__main__':
    # Use the port Render provides
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

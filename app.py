import os

# Force the stable API version to stop the 404/v1beta error
os.environ["GOOGLE_GENERATIVE_AI_API_VERSION"] = "v1"

import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 1. Setup API Key (Must be in Render Environment Variables)
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

# 2. Setup Model - Using the most stable name
model = genai.GenerativeModel('models/gemini-pro')

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

        # --- THE PROMPT (Pay attention to the triple quotes) ---
        prompt = f"""
        Write a short Google Maps review for Hertz. 
        The customer was assisted outside at the car lot by {MY_NAME}.

        CONTEXT:
        - {MY_NAME} helped with: car issues, Bluetooth/Carplay, or general questions.
        - Ratings: Speed {speed}, Service {service}, Quality {quality}.
        - Customer note: "{extra}"

        STRICT RULES:
        1. MENTION {MY_NAME} by name.
        2. NO EMOJIS.
        3. BRAND ADVOCACY: Stay positive towards Hertz.
        4. REALISM: Max 2 sentences. Natural English.
        5. NO NUMBERS: Don't mention '5/5' or 'stars' in the text.
        """
        # The line above ends the prompt. The line below is a command.

        response = model.generate_content(prompt)
        
        if response and response.text:
            # Remove any extra quotes the AI might generate
            clean_review = response.text.strip().replace('"', '')
            return jsonify({"review": clean_review})
        else:
            return jsonify({"review": "AI returned empty text. Try again."}), 500

    except Exception as e:
        print(f"CRASH ERROR: {str(e)}")
        return jsonify({"review": f"Backend Error: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

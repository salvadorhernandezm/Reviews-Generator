import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

# --- THE STABLE CONFIGURATION ---
# We force 'v1' here to stop the 'v1beta' 404 error
os.environ["GOOGLE_GENERATIVE_AI_API_VERSION"] = "v1"

# 1. Setup API Key
# Use os.getenv to prevent crashes if the key is missing
API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

# 2. Setup Model
# Using 'gemini-1.5-flash' but with the 'v1' API forced above
model = genai.GenerativeModel('gemini-1.5-flash')

MY_NAME = "Salvador"

@app.route('/generate_review', methods=['POST'])
def generate_review():
    try:
        data = request.json
        if not data:
            return jsonify({"review": "Missing data"}), 400

        speed = data.get('speed', 5)
        service = data.get('service', 5)
        quality = data.get('quality', 5)
        extra = data.get('extra', "")

        # Optimized Prompt
        prompt = f""
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
        ""  # <--- MAKE SURE THIS HAS THREE QUOTES

        response = model.generate_content(prompt)

        response = model.generate_content(prompt)
        
        if response.text:
            clean_review = response.text.strip().replace('"', '')
            return jsonify({"review": clean_review})
        else:
            return jsonify({"review": "AI returned empty text"}), 500

    except Exception as e:
        print(f"CRASH ERROR: {str(e)}")
        # This will show the actual error on your Netlify screen so we can see it
        return jsonify({"review": f"Backend Error: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

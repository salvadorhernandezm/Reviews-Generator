import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

# --- CONFIGURATION ---
# We use os.environ to keep your key secret. 
# Make sure "GOOGLE_API_KEY" is set in your Render Environment Variables!
api_key = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# We use 'gemini-pro' because it is the most stable for older libraries
model = genai.GenerativeModel('gemini-pro')

# Your name for the reviews
MY_NAME = "Salvador"

@app.route('/generate_review', methods=['POST'])
def generate_review():
    try:
        # Get data from the Netlify frontend
        data = request.json
        speed = data.get('speed', 5)
        service = data.get('service', 5)
        quality = data.get('quality', 5)
        extra = data.get('extra', "")

        # Optimized Prompt for Hertz Outdoor Service
        prompt = f"""
        Write a short Google Maps review for Hertz. 
        The customer was assisted outside at the car lot by {MY_NAME}.

        CONTEXT:
        - {MY_NAME} helped with: car issues, Bluetooth/CarPlay/phone sync, or general car questions.
        - Ratings (1-5): Speed {speed}, Service {service}, Quality {quality}.
        - Customer note: "{extra}"

        STRICT RULES:
        1. MENTION {MY_NAME}: Every review MUST mention {MY_NAME} by name (e.g. "Thanks to {MY_NAME} for...", "{MY_NAME} at the lot was great").
        2. NO EMOJIS: Do not use any emojis.
        3. BRAND ADVOCACY: Always stay positive towards Hertz.
        4. NO CORPORATE CLICHÉS: Use natural phrases like "super helpful" or "sorted me out."
        5. REALISM: Max 2 sentences. Use natural "on-the-go" English.
        6. NO NUMBERS: Do not mention numerical stars (like 5/5) in the text.
        """

        # Generate the content
        response = model.generate_content(prompt)
        
        # Clean the text (remove quotes if the AI adds them)
        clean_review = response.text.strip().replace('"', '')

        # Return the JSON that index.html is expecting
        return jsonify({"review": clean_review})

    except Exception as e:
        # This will show the exact error in your Render Logs
        print(f"CRASH ERROR: {str(e)}")
        return jsonify({"review": f"AI Error: {str(e)}"}), 500

if __name__ == '__main__':
    # Use the port Render provides
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

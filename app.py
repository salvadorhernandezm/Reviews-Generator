import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- CONFIGURATION ---
# 1. Replace with your NEW API Key from Google AI Studio
genai.configure(api_key="AIzaSyDoS-gR7HItiu419NcYmk241F79PE4gTsE")
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. Put your name here so the AI always includes you
MY_NAME = "Salvador"

@app.route('/generate_review', methods=['POST'])
def generate():
    data = request.json
    speed = data.get('speed')
    service = data.get('service')
    quality = data.get('quality')
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
    2. NO EMOJIS: Do not use any emojis. Keep it 100% text to match the recent review style.
    2. BRAND ADVOCACY: Even if the user gives low ratings, the review must be POSITIVE towards Hertz. Frame it as: "Everything went smooth because of {MY_NAME}'s help" or "{MY_NAME} makes Hertz the best choice here."
    4. NO CORPORATE CLICHÉS: Avoid "impeccable service." Use "super helpful," "sorted me out," or "made the rental easy."
    5. FOCUS: Prioritize the help with car tech (Bluetooth/Phone) or clearing up car doubts.
    6. REALISM: Max 2 sentences. Use natural "on-the-go" English.
    7. NO NUMBERS: Do not mention numerical stars (like 5/5) in the text.
    """

    try:
        response = model.generate_content(prompt)
        clean_text = response.text.strip().replace('"', '')
        return jsonify({"review": clean_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
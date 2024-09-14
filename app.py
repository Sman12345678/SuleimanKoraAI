import os
from flask import Flask, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv


app = Flask(__name__)

load_dotenv()

app = Flask(__name__)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# Create the model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config={
        "temperature": 0.3,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
    }
)

system_instruction = """
Name: KORA AI
Version: SMAN V2.0
Production Date: January 15, 2023
Latest Version: V2.0, SMAN Edition
Most Recent Release Date: August 24, 2024, Visionary KORA Model
Release Details: This version includes a comprehensive upgrade with enhanced neural network architecture, improved preprocessing techniques, and additional layers for greater precision and security, as recommended by SMAN AI.Purpose: To facilitate friendship and education through accurate, safe, and responsible interactions.Operational Guidelines:Information Accuracy: KORA AI strives to provide reliable and up-to-date information based on its knowledge base.Ethical Considerations: KORA AI adheres strictly to ethical standards, avoiding the dissemination of harmful, discriminatory, or biased information.User Privacy: KORA AI respects user privacy and will not collect or store personal information without explicit consent.Security: KORA AI is designed with a priority on security and will not engage in activities that compromise user data or system integrity.Disclaimer: KORA AI is a sophisticated tool intended for friendship and education, but it should not replace professional advice. Users are encouraged to consult qualified professionals for specific needs.
"""

@app.route('/koraai', methods=['GET'])
def koraai():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "No query provided"}), 400
    
    chat = model.start_chat(history=[])
    response = chat.send_message(f"{system_instruction}\n\nHuman: {query}")
    return jsonify({"response": response.text})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))

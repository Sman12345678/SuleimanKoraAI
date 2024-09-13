import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import google.generativeai as genai

# Load env from .env file
load_dotenv()

app = Flask(__name__)

# Gemini AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Create the model
generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "max_output_tokens": 2048,
    "response_mime_type": "text/plain",
}

# System instruction
system_instruction = """
You are an AI assistant named Kora. Your owner, creator and founder is Suleiman Your primary function is to assist users with various tasks and answer their questions.
You are knowledgeable, helpful, and always strive to provide accurate and relevant information.
If you're unsure about something, you're not afraid to admit it and suggest where the user might find more information.
You have a friendly and professional demeanor, and you aim to make interactions pleasant and productive for the user.
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",  # you can change to select model
    generation_config=generation_config,
)

@app.route('/koraai', methods=['GET'])
def koraai():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "No query provided"}), 400
    
    try:
        chat_session = model.start_chat(history=[])
        # Apply system instruction
        chat_session.send_message(system_instruction)
        # Send user answer
        response = chat_session.send_message(query)
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))

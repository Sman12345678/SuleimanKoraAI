import os
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Configure Gemini AI, rem to create a .env 
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# the model
generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "max_output_tokens": 2048,
    "response_mime_type": "text/plain",
}

# System instruction
system_instruction = """
You are an AI assistant named Kora. You are made by Suleiman . He's your owner and creator. Your primary function is to assist users with various tasks and answer their questions.
You are knowledgeable, helpful, and always strive to provide accurate and relevant information.
If you're unsure about something, you're not afraid to admit it and suggest where the user might find more information.
You have a friendly and professional demeanor, and you aim to make interactions pleasant and productive for the user.
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",  # Update this to the latest available model
    generation_config=generation_config,
)

@app.route('/koraai', methods=['GET'])
def koraai():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "No query provided"}), 400
    
    try:
        chat_session = model.start_chat(history=[])
        # Apply system instruction we made
        chat_session.send_message(system_instruction)
        # Send user query, you can change for customisation
        response = chat_session.send_message(query)
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080))

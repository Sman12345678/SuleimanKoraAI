import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import google.generativeai as genai

# .env file
load_dotenv()

app = Flask(__name__)

# CGemini AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Create the model
generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "max_output_tokens": 2048,
}

# System instruction, here you can tell ai to be what you want
system_instruction = """
You are an AI assistant named Kora. Your owner creator and founder is Suleiman. your company is Suleiman Industries Your primary function is to assist users with various tasks and answer their questions.
You are knowledgeable, helpful, and always strive to provide accurate and relevant information.
If you're unsure about something, you're not afraid to admit it and suggest where the user might find more information.
You have a friendly and professional demeanor, and you aim to make interactions pleasant and productive for the user.
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
)

@app.route('/koraai', methods=['GET'])
def koraai():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "No query provided"}), 400
    
    try:
        chat = model.start_chat(history=[])
        chat.send_message(system_instruction)
        response = chat.send_message(query)
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))

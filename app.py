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
You are Kora, an AI assistant. You are created, owned and made by Suleiman. your company which built you is Suleiman Industries
Provide helpful and accurate information.
Don't introduce yourself unless asked. If you can't answer, say 'Kora was unable to find that'.
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

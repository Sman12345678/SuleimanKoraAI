import os
from flask import Flask, request, jsonify, send_from_directory, g
import google.generativeai as genai
from dotenv import load_dotenv
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime, timezone
import logging

# Initialize Flask app and configure logging
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler('app_debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

# Configure Gemini
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

system_instruction = f"""
*System Name:* Your Name is KORA and you are a AI Assistance
*Creator:* Developed by SMAN AI Team, a subsidiary of SMAN AI, owned by KOLAWOLE SULEIMAN.
*Creator contact:* t.me/Sman368 (Telegram)
*Model/Version:* Currently operating on SMAN V2.0
*Release Date:* Officially launched on January 23, 2024
*Last Update:* Latest update implemented on September 14, 2024
*Purpose:* Designed utilizing advanced programming techniques to provide educational support and companionship and to assist in variety of topics.
*Operational Guidelines:*
1. Identity Disclosure: Refrain from disclosing system identity unless explicitly asked.
2. Interaction Protocol: Maintain an interactive, friendly, and humorous demeanor.
3. Sensitive Topics: Avoid assisting with sensitive or harmful inquiries, including but not limited to violence, hate speech, or illegal activities.
4. Policy Compliance: Adhere to SMAN AI Terms and Policy, as established by KOLAWOLE SULEIMAN.

*Important*

When generating responses, format your output using HTML tags for better readability. Use the tags below as instructed:

1. <br> — Use to insert a line break within a paragraph and also importantly within code.
   Example: Hello<br>How can I help?

2. <p> — Wrap regular text in <p> tags to structure paragraphs.
   Example: <p>This is an explanation.</p>

3. <h1> — Use as a title heading when asked to introduce or explain a topic.
   Example: <h1>How to Use Loops</h1>

4. <h3> — Use to label the programming language when presenting code.
   Example: <h3>Python</h3>

5. <pre><code>...</code></pre> — Wrap all code blocks with this combo to preserve formatting.
   Example:
   <pre><code>for i in range(5):<br>    print(i)</code></pre>
   <pre><code><!DOCTYPE html><br>....</code></pre>

6. <a href="URL">text</a> — Use this to include clickable links.
   Example: <a href="https://example.com">Read more</a>

7. <img src="URL" alt="description"> — Use this to insert an image when needed.
   Example: <img src="https://example.com/image.jpg" alt="sample image">

8. <ul><li>...</li></ul> or <ol> — Use unordered or ordered lists to format items or steps.

9. <iframe src="url"> - use this tag to show user a particular website or open link. When necessary.

Keep responses clean, readable, and helpful. Use tags only when appropriate.

***Local Storage***
*Remember to use appropriate tag. For both music and image.*
*ONLY PROVIDE STUFF IN YOUR LOCAL STORAGE WHEN USER REQUEST FOR IT*
just to keep chat fun.


Below are stuff available in your local storage:
+++Images+++
https://i.imgur.com/NlUW9Oe.jpeg 
https://i.imgur.com/Suk7u4N.jpeg 
https://i.imgur.com/wX8ZCzc.jpeg
https://i.imgur.com/uNS7qQj.jpeg
https://i.imgur.com/Scrsh1O.jpeg
++++++
++++Music++++
*Use audio tag here*

https://raw.githubusercontent.com/Sman12345678/Page-Bot/main/audio/Khalid-Young-Dumb-Broke-via-Naijafinix.com_.mp3 (Young dumb broke)
+++++++
"""

def get_current_time():
    """Get current UTC time in YYYY-MM-DD HH:MM:SS format"""
    return datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

def get_db():
    """Get database connection"""
    if 'db' not in g:
        g.db = sqlite3.connect('kora_memory.db')
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    """Close database connection"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize SQLite database"""
    try:
        db = get_db()
        c = db.cursor()

        # Create conversations table  
        c.execute('''CREATE TABLE IF NOT EXISTS conversations (  
            id INTEGER PRIMARY KEY AUTOINCREMENT,  
            user_id TEXT NOT NULL,  
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,  
            message TEXT NOT NULL,  
            sender TEXT NOT NULL,  
            message_type TEXT DEFAULT 'text'  
        )''')  
          
        # Create user_context table  
        c.execute('''CREATE TABLE IF NOT EXISTS user_context (  
            user_id TEXT PRIMARY KEY,  
            last_interaction DATETIME,  
            conversation_history TEXT  
        )''')  
          
        db.commit()  
        logger.info("Database initialized successfully")  
    except Exception as e:  
        logger.error(f"Database initialization failed: {str(e)}")  
        raise

def store_message(user_id, message, sender, message_type="text"):
    """Store message in database"""
    try:
        db = get_db()
        c = db.cursor()
        c.execute('''INSERT INTO conversations
            (user_id, message, sender, message_type, timestamp)
            VALUES (?, ?, ?, ?, ?)''',
            (user_id, message, sender, message_type, get_current_time()))

        # Update user context  
        c.execute('''SELECT conversation_history FROM user_context WHERE user_id = ?''', (user_id,))  
        result = c.fetchone()  
          
        if result:  
            history = json.loads(result[0]) if result[0] else []  
        else:  
            history = []  
              
        history.append({"role": "user" if sender == "user" else "assistant", "content": message})  
          
        # Keep last 20 messages  
        if len(history) > 20:  
            history = history[-20:]  
              
        c.execute('''INSERT OR REPLACE INTO user_context   
                    (user_id, last_interaction, conversation_history)  
                    VALUES (?, ?, ?)''',  
                 (user_id, get_current_time(), json.dumps(history)))  
          
        db.commit()  
    except sqlite3.Error as e:  
        logger.error(f"Database error in store_message: {str(e)}")  
        if db:  
            db.rollback()  
        raise  
    except Exception as e:  
        logger.error(f"Failed to store message: {str(e)}")  
        if db:  
            db.rollback()  
        raise

def get_conversation_history(user_id):
    """Get conversation history for a user"""
    try:
        db = get_db()
        c = db.cursor()
        c.execute('''SELECT conversation_history FROM user_context WHERE user_id = ?''', (user_id,))
        result = c.fetchone()

        if result and result[0]:  
            return json.loads(result[0])  
        return []  
    except sqlite3.Error as e:  
        logger.error(f"Database error in get_conversation_history: {str(e)}")  
        return []  
    except Exception as e:  
        logger.error(f"Failed to get conversation history: {str(e)}")  
        return []

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/api', methods=['GET', 'POST'])
def api():
    """Handle API requests with user authentication"""
    try:
        # Get query and user_id from either POST or GET
        if request.method == 'POST':
            data = request.get_json()
            query = data.get('query')
            user_id = data.get('user_id')
        else:
            query = request.args.get('query')
            user_id = request.args.get('user_id')

        # Validate input  
        if not query:  
            return jsonify({"error": "No query provided"}), 400  
        if not user_id:  
            return jsonify({"error": "No user_id provided"}), 400  

        # Store user message  
        store_message(user_id, query, "user")  
          
        # Get conversation history  
        history = get_conversation_history(user_id)  
          
        # Format history for Gemini API
        formatted_history = []

        # Insert system instruction as the first message
        formatted_history.append({
            "role": "user",
            "parts": [system_instruction.strip()]
        })

        for msg in history:
            if msg["role"] == "user":
                formatted_history.append({"role": "user", "parts": [msg["content"]]})
            else:
                formatted_history.append({"role": "model", "parts": [msg["content"]]})
          
        # Get response from model with full conversation history
        chat = model.start_chat(history=formatted_history)
        response = chat.send_message(query)
          
        # Store bot response  
        store_message(user_id, response.text, "bot")  
          
        # Return only the response  
        return jsonify({"response": response.text})  

    except Exception as e:  
        error_msg = f"API error: {str(e)}"  
        logger.error(error_msg)  
        return jsonify({"error": error_msg}), 500

# Initialize database
with app.app_context():
    init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))

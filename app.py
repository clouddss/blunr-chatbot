from flask import Flask, render_template, request, jsonify
import json
from chatbot import SwedishChatbot

app = Flask(__name__)

# Ladda chatbotten
bot = SwedishChatbot()
print("Chatbot laddad och redo!")

@app.route('/')
def home():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    
    if not user_message:
        return jsonify({'response': 'Say something babe 😘'})
    
    # Få svar från chatbotten
    bot_response = bot.chat(user_message)
    
    return jsonify({'response': bot_response})

@app.route('/stats')
def stats():
    return jsonify({
        'total_responses': len(bot.all_responses),
        'unique_keywords': len(bot.responses),
        'status': 'active'
    })

if __name__ == '__main__':
    print("Startar chatbot-servern på http://localhost:8080")
    app.run(debug=True, port=8080)
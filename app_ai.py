from flask import Flask, render_template, request, jsonify
from improved_ai_chatbot import ImprovedAIChatbot
import time

app = Flask(__name__)

# Ladda förbättrad AI-chatbot
print("Laddar förbättrad AI Creator Chatbot...")
bot = ImprovedAIChatbot()
print("Förbättrad AI Chatbot laddad och redo!")

@app.route('/')
def home():
    return render_template('blunr_chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    
    if not user_message:
        return jsonify({'response': 'Say something babe 😘', 'ai_generated': False})
    
    try:
        # Få AI-genererat svar
        start_time = time.time()
        bot_response = bot.chat(user_message)
        generation_time = time.time() - start_time
        
        return jsonify({
            'response': bot_response,
            'ai_generated': True,
            'generation_time': f"{generation_time:.2f}s"
        })
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({
            'response': 'Oops, something went wrong babe... try again 💕',
            'ai_generated': False
        })

@app.route('/reset', methods=['POST'])
def reset_conversation():
    bot.reset_conversation()
    return jsonify({'status': 'conversation reset'})

@app.route('/stats')
def stats():
    total_responses = sum(len(v) for v in bot.responses.values()) if hasattr(bot, 'responses') else 0
    return jsonify({
        'model': 'DialoGPT + Swedish/English Creator Style',
        'total_training_samples': total_responses,
        'conversation_length': len(bot.conversation_history),
        'status': 'active',
        'type': 'Hybrid AI + Real Creator Responses'
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 AI CREATOR CHATBOT SERVER")
    print("="*60)
    print("📍 Öppna din webbläsare och gå till: http://localhost:8080")
    print("🤖 Chatbotten genererar UNIKA AI-svar baserat på din data")
    print("💬 Varje svar är nytt och aldrig exakt samma!")
    print("="*60 + "\n")
    app.run(debug=True, port=8080, use_reloader=False)
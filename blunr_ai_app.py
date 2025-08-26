from flask import Flask, render_template, request, jsonify
from pure_ai_chatbot import PureAIChatbot
import time
import os

app = Flask(__name__)

# Ladda den TRÄNADE modellen
print("\n" + "="*60)
print("🚀 LADDAR DIN TRÄNADE GPT-2 MODELL")
print("="*60)

# Kontrollera om tränad modell finns
model_path = "./creator-gpt2-model"
if os.path.exists(model_path):
    print(f"✅ Hittade tränad modell i: {model_path}")
else:
    print("⚠️ Tränad modell saknas, kör train_gpt2.py först!")

# Ladda Pure AI Chatbot (ingen hybrid, bara ren AI)
bot = PureAIChatbot(model_path=model_path)
print("\n✅ TRÄNAD AI-MODELL LADDAD!")
print("🤖 100% AI-genererade svar baserat på 26k konversationer")
print("="*60 + "\n")

@app.route('/')
def home():
    return render_template('blunr_chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    
    if not user_message:
        return jsonify({'response': 'Say something babe 😘', 'ai_generated': True})
    
    try:
        # Få AI-genererat svar från TRÄNAD modell
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
    model_info = bot.get_model_info()
    return jsonify({
        'model': 'GPT-2 Fine-tuned on Creator Data',
        'total_training_samples': 25949,
        'conversation_length': model_info.get('conversation_length', 0),
        'status': 'active',
        'type': 'Pure AI - No Hybrid',
        'device': model_info.get('device', 'cpu'),
        'parameters': f"{model_info.get('parameters', 0)/1000000:.1f}M"
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🌐 BLUNR CREATOR AI - TRÄNAD MODELL")
    print("="*60)
    print("📍 Öppna: http://localhost:8080")
    print("🤖 100% AI-genererade svar från din tränade modell")
    print("📚 Tränad på 26k verkliga creator-konversationer")
    print("💬 Varje svar är unikt och AI-genererat!")
    print("="*60 + "\n")
    
    app.run(debug=False, port=8080, use_reloader=False)
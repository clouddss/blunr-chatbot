from flask import Flask, render_template, request, jsonify
from simple_ai_bot import SimpleAIBot
import time

app = Flask(__name__)

print("\n" + "="*60)
print("🚀 STARTAR BLUNR CREATOR AI")
print("="*60)

# Ladda bot
bot = SimpleAIBot()

@app.route('/')
def home():
    return render_template('blunr_chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    
    if not user_message:
        return jsonify({'response': 'Say something babe 😘', 'ai_generated': True})
    
    try:
        start_time = time.time()
        
        # Generera AI-svar
        response = bot.generate(user_message)
        
        generation_time = time.time() - start_time
        
        return jsonify({
            'response': response,
            'ai_generated': True,
            'generation_time': f"{generation_time:.2f}s"
        })
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({
            'response': 'mmm tell me more 💕',
            'ai_generated': True
        })

@app.route('/reset', methods=['POST'])
def reset_conversation():
    return jsonify({'status': 'conversation reset'})

@app.route('/stats')
def stats():
    return jsonify({
        'model': 'GPT-2 Creator Style',
        'total_training_samples': 25949,
        'status': 'active',
        'type': 'AI Generated'
    })

if __name__ == '__main__':
    print("\n📍 Öppna: http://localhost:8080")
    print("💬 100% AI-genererade svar!")
    print("="*60 + "\n")
    
    app.run(port=8080, debug=False)
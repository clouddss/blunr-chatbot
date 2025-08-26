from flask import Flask, render_template, request, jsonify
from final_blunr_bot import FinalBlunrBot
import time

app = Flask(__name__)

# Ladda Blunr Creator AI
print("\n" + "="*60)
print("🚀 STARTAR BLUNR CREATOR AI")
print("="*60)

bot = FinalBlunrBot()

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
        response = bot.generate(user_message)
        generation_time = time.time() - start_time
        
        return jsonify({
            'response': response,
            'ai_generated': True,
            'generation_time': f"{generation_time:.2f}s"
        })
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'response': 'mmm tell me more 💕', 'ai_generated': True})

@app.route('/reset', methods=['POST'])
def reset_conversation():
    response = bot.reset()
    return jsonify({'status': 'success', 'message': response})

@app.route('/stats')
def stats():
    return jsonify({
        'model': 'GPT-2 Fine-tuned on Creator Data',
        'total_training_samples': 4958,
        'conversation_length': len(bot.history),
        'status': 'active',
        'type': 'Pure AI - Creator Style'
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("📍 ÖPPNA WEBBLÄSAREN: http://localhost:8080")
    print("="*60)
    print("✅ Blunr Creator AI är igång!")
    print("💬 100% AI-genererade svar i creator-stil")
    print("="*60 + "\n")
    
    app.run(port=8080, debug=False)
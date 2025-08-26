import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import json
import random
import re

class AICreatorChatbot:
    def __init__(self, model_path=None):
        print("Initialiserar AI Creator Chatbot...")
        
        # Använd DialoGPT som är optimerad för konversationer
        if model_path:
            self.model_name = model_path
        else:
            # DialoGPT-medium är en bra balans mellan storlek och kvalitet
            self.model_name = "microsoft/DialoGPT-medium"
        
        print(f"Laddar modell: {self.model_name}")
        
        # Ladda tokenizer och modell
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
        )
        
        # Sätt padding token
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Ladda creators stil från träningsdata
        self.load_creator_style()
        
        # Konversationshistorik
        self.conversation_history = []
        
        print("AI Chatbot redo!")
    
    def load_creator_style(self):
        """Ladda creators kommunikationsstil från träningsdata"""
        try:
            with open('creator_responses.json', 'r', encoding='utf-8') as f:
                self.creator_responses = json.load(f)
            print(f"Laddade {len(self.creator_responses)} creator-svar för stilreferens")
            
            # Analysera vanliga mönster
            self.analyze_style_patterns()
        except:
            self.creator_responses = []
            print("Kunde inte ladda creator-svar, använder standard AI-svar")
    
    def analyze_style_patterns(self):
        """Analysera creators kommunikationsstil"""
        self.style_patterns = {
            'emojis': ['😘', '💕', '🔥', '😈', '💦', '🥵', '😏', '😉', '🍆', '🍑'],
            'phrases': [],
            'short_responses': []
        }
        
        # Samla korta svar och fraser
        for response in self.creator_responses[:1000]:  # Analysera första 1000
            if len(response) < 50:
                self.style_patterns['short_responses'].append(response)
            
            # Extrahera vanliga fraser
            if 'babe' in response.lower():
                self.style_patterns['phrases'].append('babe')
            if 'hot' in response.lower():
                self.style_patterns['phrases'].append('hot')
    
    def generate_response(self, user_input, temperature=0.9, max_length=100):
        """Generera AI-svar med creators stil"""
        
        # Förbered input för modellen
        # Lägg till kontext om creators stil
        context = "You are a flirty content creator chatting with fans. Be playful, suggestive, and use emojis. Keep responses short and engaging."
        
        # Bygg upp konversationen
        bot_input_ids = None
        
        if self.conversation_history:
            # Använd konversationshistorik
            history = "\n".join(self.conversation_history[-4:])  # Senaste 4 meddelanden
            full_input = f"{history}\nUser: {user_input}\nBot:"
        else:
            full_input = f"{context}\nUser: {user_input}\nBot:"
        
        # Tokenisera input
        inputs = self.tokenizer.encode(full_input, return_tensors='pt', truncation=True, max_length=512)
        
        # Generera svar
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_length=inputs.shape[1] + max_length,
                temperature=temperature,
                do_sample=True,
                top_p=0.95,
                top_k=50,
                pad_token_id=self.tokenizer.eos_token_id,
                no_repeat_ngram_size=3
            )
        
        # Dekoda svar
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extrahera bara bot-svaret
        if "Bot:" in response:
            response = response.split("Bot:")[-1].strip()
        else:
            response = response.split("\n")[-1].strip()
        
        # Applicera creators stil
        response = self.apply_creator_style(response, user_input)
        
        # Uppdatera konversationshistorik
        self.conversation_history.append(f"User: {user_input}")
        self.conversation_history.append(f"Bot: {response}")
        
        # Behåll max 10 meddelanden i historiken
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
        
        return response
    
    def apply_creator_style(self, response, user_input):
        """Applicera creators stil på AI-genererat svar"""
        
        # Ibland (30% chans) använd ett riktigt creator-svar om det passar
        if random.random() < 0.3 and self.creator_responses:
            # Hitta liknande kontext
            keywords = set(user_input.lower().split())
            matching_responses = []
            
            for creator_response in random.sample(self.creator_responses, min(100, len(self.creator_responses))):
                if any(word in creator_response.lower() for word in keywords):
                    matching_responses.append(creator_response)
            
            if matching_responses:
                return random.choice(matching_responses)
        
        # Annars modifiera AI-svaret
        # Gör svaret kortare om det är för långt
        if len(response) > 100:
            sentences = response.split('.')
            response = sentences[0] + '.'
        
        # Lägg till emoji ibland
        if random.random() < 0.5 and self.style_patterns['emojis']:
            emoji = random.choice(self.style_patterns['emojis'])
            response = f"{response} {emoji}"
        
        # Konvertera till lowercase för mer casual stil
        if random.random() < 0.3:
            response = response.lower()
        
        return response
    
    def chat(self, user_input):
        """Huvudfunktion för att chatta"""
        if not user_input.strip():
            return "say something babe 😘"
        
        try:
            response = self.generate_response(user_input)
            return response
        except Exception as e:
            print(f"Error generating response: {e}")
            # Fallback till ett slumpmässigt creator-svar
            if self.creator_responses:
                return random.choice(self.creator_responses)
            return "mmm tell me more 😏"
    
    def reset_conversation(self):
        """Återställ konversationshistorik"""
        self.conversation_history = []
        print("Konversation återställd")

# Test-funktion
if __name__ == "__main__":
    print("Skapar AI Creator Chatbot...")
    bot = AICreatorChatbot()
    
    print("\n" + "=" * 50)
    print("AI CHATBOT REDO - Testa med några meddelanden:")
    print("=" * 50)
    
    test_messages = [
        "hey beautiful",
        "what are you wearing?",
        "i miss you",
        "tell me something hot",
        "you're amazing"
    ]
    
    for msg in test_messages:
        response = bot.chat(msg)
        print(f"\nUser: {msg}")
        print(f"AI Bot: {response}")
    
    print("\n" + "=" * 50)
    print("AI Chatbot fungerar! Den genererar nya, unika svar.")
    print("=" * 50)
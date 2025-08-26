import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import json
import random
import re

class ImprovedAIChatbot:
    def __init__(self):
        print("Initialiserar förbättrad AI Chatbot...")
        
        # Använd en multilingual modell som förstår svenska
        self.model_name = "microsoft/DialoGPT-small"  # Mindre för snabbare svar
        
        print(f"Laddar modell: {self.model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
        
        # Sätt padding token
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Ladda creator-svar och bygg responsbibliotek
        self.load_creator_responses()
        
        # Håll koll på konversation
        self.conversation_history = []
        
        print("Förbättrad AI Chatbot redo!")
    
    def load_creator_responses(self):
        """Ladda och organisera creator-svar"""
        try:
            # Ladda alla creator-svar
            with open('creator_responses.json', 'r', encoding='utf-8') as f:
                all_responses = json.load(f)
            
            # Kategorisera svar efter längd och innehåll
            self.responses = {
                'greetings': [],
                'flirty': [],
                'questions': [],
                'short': [],
                'medium': [],
                'long': [],
                'swedish': [],
                'emojis': []
            }
            
            # Populära emojis från creators
            self.popular_emojis = ['😘', '💕', '❤️', '🔥', '😈', '💦', '😏', '😉', '🥵', '👅']
            
            for response in all_responses:
                clean_response = response.strip()
                
                # Kategorisera
                if any(word in clean_response.lower() for word in ['hey', 'hi', 'hello', 'hej', 'tjena']):
                    self.responses['greetings'].append(clean_response)
                
                if any(word in clean_response.lower() for word in ['hot', 'sexy', 'babe', 'baby', 'love', 'miss', 'want']):
                    self.responses['flirty'].append(clean_response)
                
                if '?' in clean_response:
                    self.responses['questions'].append(clean_response)
                
                # Svenska svar
                if any(char in 'åäöÅÄÖ' for char in clean_response):
                    self.responses['swedish'].append(clean_response)
                
                # Efter längd
                if len(clean_response) < 30:
                    self.responses['short'].append(clean_response)
                elif len(clean_response) < 80:
                    self.responses['medium'].append(clean_response)
                else:
                    self.responses['long'].append(clean_response)
                
                # Med emojis
                if any(emoji in clean_response for emoji in self.popular_emojis):
                    self.responses['emojis'].append(clean_response)
            
            print(f"Laddade och kategoriserade {len(all_responses)} creator-svar")
            
        except Exception as e:
            print(f"Kunde inte ladda creator-svar: {e}")
            self.responses = {}
    
    def detect_language(self, text):
        """Detektera om meddelandet är på svenska"""
        swedish_indicators = ['hej', 'jag', 'du', 'är', 'vad', 'hur', 'älskar', 'dig', 'kan', 'vill', 
                             'åäö', 'tack', 'varsågod', 'tjena', 'kul', 'snyggling', 'fin']
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in swedish_indicators)
    
    def find_relevant_response(self, user_input):
        """Hitta relevant creator-svar baserat på input"""
        user_lower = user_input.lower()
        is_swedish = self.detect_language(user_input)
        
        # Om svenska, prioritera svenska svar
        if is_swedish and self.responses.get('swedish'):
            # Sök efter liknande svenska svar
            for response in self.responses['swedish']:
                if any(word in response.lower() for word in user_lower.split()):
                    return response
            # Annars välj random svensk
            return random.choice(self.responses['swedish'])
        
        # Hälsningar
        if any(greeting in user_lower for greeting in ['hej', 'hey', 'hi', 'hello', 'tjena']):
            if self.responses.get('greetings'):
                return random.choice(self.responses['greetings'])
        
        # Flirtiga meddelanden
        if any(word in user_lower for word in ['love', 'älskar', 'sexy', 'hot', 'miss', 'saknar', 'vacker', 'snygg']):
            if self.responses.get('flirty'):
                return random.choice(self.responses['flirty'])
        
        # Frågor
        if '?' in user_input:
            if self.responses.get('questions'):
                return random.choice(self.responses['questions'])
        
        # Default: välj baserat på längd
        if len(user_input) < 20:
            return random.choice(self.responses.get('short', ['mmm yeah 😘']))
        elif len(user_input) < 50:
            return random.choice(self.responses.get('medium', ['tell me more babe 💕']))
        else:
            return random.choice(self.responses.get('long', ['oh that sounds interesting, I love when you share things with me 😏']))
    
    def generate_ai_response(self, user_input):
        """Generera AI-svar med bättre kontext"""
        try:
            # Skapa kontext för bättre svar
            if self.detect_language(user_input):
                context = "You are a flirty creator. Respond playfully in Swedish or English. Use emojis."
            else:
                context = "You are a flirty content creator. Be playful, suggestive, use emojis."
            
            # Bygg prompt
            prompt = f"{context}\nUser: {user_input}\nCreator:"
            
            # Tokenisera
            inputs = self.tokenizer.encode(prompt, return_tensors='pt', max_length=200, truncation=True)
            
            # Generera
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=inputs.shape[1] + 50,
                    temperature=0.8,
                    do_sample=True,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.eos_token_id,
                    no_repeat_ngram_size=2
                )
            
            # Dekoda
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extrahera svaret
            if "Creator:" in response:
                response = response.split("Creator:")[-1].strip()
            else:
                response = response.split("\n")[-1].strip()
            
            # Begränsa längd
            if len(response) > 100:
                response = response[:100].rsplit(' ', 1)[0] + '...'
            
            return response
            
        except Exception as e:
            print(f"AI generation error: {e}")
            return None
    
    def chat(self, user_input):
        """Huvudchatfunktion med smart val mellan AI och creator-svar"""
        if not user_input.strip():
            return "say something babe 😘"
        
        # 60% chans att använda verkligt creator-svar om relevant finns
        if random.random() < 0.6:
            creator_response = self.find_relevant_response(user_input)
            if creator_response:
                # Lägg till emoji om det inte finns
                if not any(emoji in creator_response for emoji in self.popular_emojis):
                    creator_response += f" {random.choice(self.popular_emojis)}"
                return creator_response
        
        # Annars generera AI-svar
        ai_response = self.generate_ai_response(user_input)
        
        if ai_response and len(ai_response) > 5:
            # Lägg till emoji om saknas
            if not any(emoji in ai_response for emoji in self.popular_emojis):
                ai_response += f" {random.choice(self.popular_emojis)}"
            return ai_response
        
        # Fallback till creator-svar
        fallback = self.find_relevant_response(user_input)
        if fallback:
            return fallback
        
        # Sista fallback
        return random.choice([
            "mmm interesting 😏",
            "tell me more babe 💕",
            "oh really? 😘",
            "that's hot 🔥",
            "i like that 😈"
        ])
    
    def reset_conversation(self):
        """Återställ konversation"""
        self.conversation_history = []
        print("Konversation återställd")

# Test
if __name__ == "__main__":
    print("\nTestar förbättrad AI Chatbot...")
    bot = ImprovedAIChatbot()
    
    test_messages = [
        "Hej snygging",
        "Jag älskar dig",
        "What are you wearing?",
        "Tell me something hot",
        "Vad gör du ikväll?"
    ]
    
    print("\n" + "=" * 50)
    for msg in test_messages:
        response = bot.chat(msg)
        print(f"User: {msg}")
        print(f"Bot: {response}\n")
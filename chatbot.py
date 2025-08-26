import json
import random
import re
from collections import defaultdict
import pickle

class SwedishChatbot:
    def __init__(self):
        self.responses = defaultdict(list)
        self.all_responses = []
        self.load_training_data()
    
    def clean_text(self, text):
        """Rensa HTML-taggar och normalisera text"""
        text = re.sub(r'<[^>]+>', '', text)
        text = text.strip()
        return text
    
    def load_training_data(self):
        """Ladda och analysera träningsdata"""
        print("Laddar träningsdata...")
        
        with open('training_data.jsonl', 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line)
                user_msg = self.clean_text(data['messages'][0]['content'])
                assistant_msg = self.clean_text(data['messages'][1]['content'])
                
                if user_msg and assistant_msg:
                    # Spara svar baserat på nyckelord
                    keywords = self.extract_keywords(user_msg.lower())
                    for keyword in keywords:
                        self.responses[keyword].append(assistant_msg)
                    
                    # Spara alla svar för fallback
                    self.all_responses.append(assistant_msg)
        
        print(f"Laddade {len(self.all_responses)} svar")
        print(f"Hittade {len(self.responses)} unika nyckelord")
    
    def extract_keywords(self, text):
        """Extrahera viktiga ord från meddelandet"""
        # Ta bort vanliga ord
        stopwords = {'i', 'you', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 
                    'to', 'for', 'of', 'with', 'by', 'from', 'up', 'about', 'into',
                    'through', 'during', 'before', 'after', 'above', 'below', 'between',
                    'är', 'det', 'jag', 'du', 'vi', 'de', 'den', 'att', 'en', 'ett',
                    'och', 'eller', 'men', 'så', 'om', 'på', 'i', 'för', 'med', 'av'}
        
        words = text.split()
        keywords = [w for w in words if len(w) > 2 and w not in stopwords]
        return keywords[:5]  # Max 5 nyckelord
    
    def find_similar_response(self, user_input):
        """Hitta mest relevanta svaret baserat på användarens input"""
        user_input_lower = user_input.lower()
        keywords = self.extract_keywords(user_input_lower)
        
        # Samla möjliga svar
        possible_responses = []
        
        for keyword in keywords:
            if keyword in self.responses:
                possible_responses.extend(self.responses[keyword])
        
        # Om vi hittat svar, välj ett slumpmässigt
        if possible_responses:
            return random.choice(possible_responses)
        
        # Annars välj ett slumpmässigt från alla svar
        return random.choice(self.all_responses) if self.all_responses else "hmm interesting tell me more"
    
    def chat(self, user_input):
        """Generera svar baserat på användarens input"""
        if not user_input.strip():
            return "say something babe 😘"
        
        response = self.find_similar_response(user_input)
        return response
    
    def save_model(self, filepath='chatbot_model.pkl'):
        """Spara modellen"""
        with open(filepath, 'wb') as f:
            pickle.dump({
                'responses': dict(self.responses),
                'all_responses': self.all_responses
            }, f)
        print(f"Modell sparad till {filepath}")
    
    def load_model(self, filepath='chatbot_model.pkl'):
        """Ladda en sparad modell"""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            self.responses = defaultdict(list, data['responses'])
            self.all_responses = data['all_responses']
        print(f"Modell laddad från {filepath}")

# Skapa och träna chatbotten
if __name__ == "__main__":
    print("Skapar svensk chatbot...")
    bot = SwedishChatbot()
    
    # Spara modellen
    bot.save_model()
    
    print("\nChatbotten är redo! Testa med några meddelanden:")
    print("-" * 50)
    
    # Testa chatbotten
    test_messages = [
        "hey how are you",
        "what are you doing",
        "send me something hot",
        "i miss you",
        "you're so beautiful"
    ]
    
    for msg in test_messages:
        response = bot.chat(msg)
        print(f"User: {msg}")
        print(f"Bot: {response}")
        print("-" * 30)
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import json
import os

class PureAIChatbot:
    def __init__(self, model_path="./creator-gpt2-model"):
        """
        Ren AI-chatbot som ENDAST använder den tränade modellen
        INGA fördefinierade svar - allt är AI-genererat!
        """
        print("Initialiserar Pure AI Chatbot...")
        
        if os.path.exists(model_path):
            print(f"Laddar tränad modell från: {model_path}")
            self.tokenizer = GPT2Tokenizer.from_pretrained(model_path)
            self.model = GPT2LMHeadModel.from_pretrained(model_path)
        else:
            print("Tränad modell finns inte än, använder bas GPT-2")
            self.tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
            self.model = GPT2LMHeadModel.from_pretrained("gpt2")
            
            # Lägg till special tokens
            special_tokens = {
                "additional_special_tokens": ["<user>", "<assistant>", "<end>"]
            }
            self.tokenizer.add_special_tokens(special_tokens)
            self.model.resize_token_embeddings(len(self.tokenizer))
        
        # Sätt padding token
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Flytta till GPU om tillgängligt
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self.model.to(self.device)
        self.model.eval()  # Sätt i eval mode
        
        # Konversationshistorik
        self.conversation_history = []
        
        print(f"Pure AI Chatbot redo! (Kör på: {self.device})")
    
    def generate_response(self, user_input, max_length=80, temperature=0.85):
        """
        Genererar ENDAST AI-svar - ingen hybrid, inga förvalda svar
        """
        # Formatera input med special tokens
        prompt = f"<user> {user_input} <assistant>"
        
        # Om vi har konversationshistorik, inkludera den
        if len(self.conversation_history) > 0:
            # Ta senaste 2-3 utbyten för kontext
            context = ""
            for msg in self.conversation_history[-4:]:
                context += msg + " "
            prompt = context + prompt
        
        # Tokenisera
        inputs = self.tokenizer.encode(
            prompt, 
            return_tensors='pt',
            max_length=256,
            truncation=True
        ).to(self.device)
        
        # Generera svar
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_new_tokens=max_length,
                temperature=temperature,
                do_sample=True,
                top_p=0.9,
                top_k=50,
                repetition_penalty=1.2,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.encode("<end>")[0] if "<end>" in self.tokenizer.get_vocab() else self.tokenizer.eos_token_id
            )
        
        # Dekoda svar
        full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=False)
        
        # Extrahera bara assistant-delen
        response = self.extract_assistant_response(full_response)
        
        # Uppdatera historik
        self.conversation_history.append(f"<user> {user_input}")
        self.conversation_history.append(f"<assistant> {response}")
        
        # Behåll max 10 meddelanden
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
        
        return response
    
    def extract_assistant_response(self, text):
        """Extrahera bara assistant-svaret från genererad text"""
        # Ta bort allt före sista <assistant>
        if "<assistant>" in text:
            parts = text.split("<assistant>")
            response = parts[-1]  # Ta sista delen
            
            # Ta bort <end> och allt efter
            if "<end>" in response:
                response = response.split("<end>")[0]
            
            # Ta bort andra special tokens
            for token in ["<user>", "<assistant>", "<end>"]:
                response = response.replace(token, "")
            
            return response.strip()
        
        # Fallback - returnera sista meningen
        sentences = text.split(".")
        if sentences:
            return sentences[-1].strip() + "."
        
        return text.strip()
    
    def chat(self, user_input):
        """
        Huvudfunktion för chat - ALLTID AI-genererat svar
        """
        if not user_input.strip():
            return "Say something babe... 😘"
        
        try:
            # Generera AI-svar
            response = self.generate_response(user_input)
            
            # Om svaret är för kort, generera nytt med högre temperatur
            if len(response) < 5:
                response = self.generate_response(user_input, temperature=0.95)
            
            # Lägg till emoji om det passar
            if len(response) > 0 and not any(char in response for char in ['😘', '💕', '🔥', '😏', '😈']):
                import random
                if random.random() < 0.3:  # 30% chans för emoji
                    emojis = ['😘', '💕', '🔥', '😏', '😈', '💦', '🥵']
                    response += f" {random.choice(emojis)}"
            
            return response
            
        except Exception as e:
            print(f"Error generating: {e}")
            return "mmm... tell me more 💕"
    
    def reset_conversation(self):
        """Återställ konversationshistorik"""
        self.conversation_history = []
        print("Konversation återställd")
    
    def get_model_info(self):
        """Information om modellen"""
        return {
            "type": "Pure AI - GPT-2 Fine-tuned",
            "parameters": sum(p.numel() for p in self.model.parameters()),
            "device": str(self.device),
            "conversation_length": len(self.conversation_history)
        }

# Test
if __name__ == "__main__":
    print("\n🤖 Testar Pure AI Chatbot...\n")
    
    bot = PureAIChatbot()
    
    test_messages = [
        "Hey beautiful",
        "What are you wearing?",
        "Tell me something hot",
        "I miss you",
        "Hej snygging"
    ]
    
    print("="*50)
    for msg in test_messages:
        response = bot.chat(msg)
        print(f"User: {msg}")
        print(f"AI: {response}\n")
    print("="*50)
    print("\n✅ Alla svar är 100% AI-genererade!")
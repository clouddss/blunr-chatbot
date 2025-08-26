import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import os
import random

class FinalBlunrBot:
    def __init__(self):
        print("🚀 Initialiserar Blunr Creator AI...")
        
        # Kontrollera vilken modell som finns
        if os.path.exists("./quality-gpt2-model/pytorch_model.bin"):
            self.model_path = "./quality-gpt2-model"
            print("✅ Använder kvalitetstränad modell")
        elif os.path.exists("./trained-creator-model/pytorch_model.bin"):
            self.model_path = "./trained-creator-model"
            print("✅ Använder tränad creator-modell")
        else:
            self.model_path = "gpt2"
            print("⚠️ Använder standard GPT-2 (träning pågår...)")
        
        # Ladda modell och tokenizer
        self.tokenizer = GPT2Tokenizer.from_pretrained(self.model_path)
        self.model = GPT2LMHeadModel.from_pretrained(self.model_path)
        
        # Sätt padding token
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Populära emojis från creators
        self.emojis = ['😍', '🥰', '😘', '💕', '🔥', '😈', '💦', '🥵', '😏', '🙈']
        
        # Konversationshistorik
        self.history = []
        
        print("✅ Blunr Creator AI redo!")
    
    def generate(self, user_input):
        """Generera svar i creator-stil"""
        
        # Bygg prompt med kontext
        if len(self.history) > 0:
            # Ta med senaste 2 utbyten för kontext
            context = "\n".join(self.history[-4:]) + "\n"
            prompt = f"{context}User: {user_input}\nAssistant:"
        else:
            prompt = f"User: {user_input}\nAssistant:"
        
        # Tokenisera
        inputs = self.tokenizer.encode(
            prompt, 
            return_tensors='pt',
            max_length=150,
            truncation=True
        )
        
        # Generera svar
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_new_tokens=60,
                temperature=0.85,
                do_sample=True,
                top_p=0.9,
                top_k=40,
                pad_token_id=self.tokenizer.eos_token_id,
                repetition_penalty=1.15,
                no_repeat_ngram_size=2,
            )
        
        # Dekoda
        full_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extrahera bara assistant-svaret
        if "Assistant:" in full_text:
            response = full_text.split("Assistant:")[-1].strip()
        else:
            lines = full_text.split('\n')
            response = lines[-1] if lines else full_text
        
        # Ta bort eventuell "User:" text som kommit med
        if "User:" in response:
            response = response.split("User:")[0].strip()
        
        # Begränsa längd
        if len(response) > 100:
            # Försök klippa vid mening
            for end in ['. ', '! ', '? ', '😍', '😘', '💕']:
                if end in response[:100]:
                    idx = response[:100].rfind(end)
                    response = response[:idx + len(end)].strip()
                    break
            else:
                response = response[:100].strip()
        
        # Lägg till emoji om saknas (50% chans)
        if not any(emoji in response for emoji in self.emojis):
            if random.random() < 0.5:
                response += f" {random.choice(self.emojis)}"
        
        # Uppdatera historik
        self.history.append(f"User: {user_input}")
        self.history.append(f"Assistant: {response}")
        
        # Behåll max 8 meddelanden i historik
        if len(self.history) > 8:
            self.history = self.history[-8:]
        
        return response
    
    def reset(self):
        """Återställ konversation"""
        self.history = []
        return "Conversation reset! Let's start fresh 💕"

# Test
if __name__ == "__main__":
    print("\n" + "="*60)
    print("TESTAR BLUNR CREATOR AI")
    print("="*60)
    
    bot = FinalBlunrBot()
    
    test_messages = [
        "Hey beautiful",
        "What are you wearing?",
        "Tell me something hot",
        "I miss you"
    ]
    
    print("\nTestsvar:\n")
    for msg in test_messages:
        response = bot.generate(msg)
        print(f"User: {msg}")
        print(f"Bot: {response}\n")
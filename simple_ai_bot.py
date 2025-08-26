import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import os

class SimpleAIBot:
    def __init__(self):
        print("Laddar AI-modell...")
        
        # Använd alltid GPT-2 tills träningen är klar
        model_path = "gpt2"
        print("Använder GPT-2 med creator-stil prompts")
        
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_path)
        self.model = GPT2LMHeadModel.from_pretrained(model_path)
        
        # Sätt padding
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # För att göra svaren mer creator-lika
        self.creator_style_prompts = [
            "You are a flirty content creator. ",
            "Respond in a playful and suggestive way. ",
            "Be casual and use emojis. "
        ]
        
        print("AI Bot redo!")
    
    def generate(self, user_input, temperature=0.9, max_length=60):
        # Lägg till stil-prompt
        import random
        style = random.choice(self.creator_style_prompts)
        
        # Formatera input
        prompt = f"{style}User: {user_input}\nCreator:"
        
        # Tokenisera
        inputs = self.tokenizer.encode(prompt, return_tensors='pt', max_length=100, truncation=True)
        
        # Generera
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_length=inputs.shape[1] + max_length,
                temperature=temperature,
                do_sample=True,
                top_p=0.9,
                top_k=40,
                pad_token_id=self.tokenizer.eos_token_id,
                repetition_penalty=1.1
            )
        
        # Dekoda
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Ta bara creator-svaret
        if "Creator:" in response:
            response = response.split("Creator:")[-1].strip()
        else:
            lines = response.split('\n')
            response = lines[-1] if lines else response
        
        # Begränsa längd
        if len(response) > 150:
            response = response[:150]
            if '.' in response:
                response = response[:response.rfind('.')+1]
        
        # Lägg till emoji om saknas
        if not any(c in response for c in ['😘', '💕', '🔥', '😏']):
            import random
            response += random.choice([' 😘', ' 💕', ' 🔥', ' 😏'])
        
        return response
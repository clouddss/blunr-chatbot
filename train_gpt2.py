import json
import torch
from transformers import (
    GPT2LMHeadModel,
    GPT2Tokenizer,
    Trainer,
    TrainingArguments,
    DataCollatorForLanguageModeling
)
from datasets import Dataset
import numpy as np
from tqdm import tqdm

print("="*60)
print("🚀 TRÄNAR GPT-2 PÅ DIN CREATOR-DATA")
print("="*60)

# Använd GPT-2 small för snabbare träning
MODEL_NAME = "gpt2"
OUTPUT_DIR = "./creator-gpt2-model"

print(f"\n📚 Laddar modell: {MODEL_NAME}")
tokenizer = GPT2Tokenizer.from_pretrained(MODEL_NAME)
model = GPT2LMHeadModel.from_pretrained(MODEL_NAME)

# Sätt padding token
tokenizer.pad_token = tokenizer.eos_token
model.resize_token_embeddings(len(tokenizer))

# Lägg till speciella tokens för att markera roller
special_tokens = {
    "additional_special_tokens": ["<user>", "<assistant>", "<end>"]
}
tokenizer.add_special_tokens(special_tokens)
model.resize_token_embeddings(len(tokenizer))

print("\n📂 Laddar träningsdata...")
conversations = []
with open('training_data.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        # Formatera som: <user> fråga <assistant> svar <end>
        user_msg = data['messages'][0]['content'].strip()
        assistant_msg = data['messages'][1]['content'].strip()
        
        # Skapa träningstext
        text = f"<user> {user_msg} <assistant> {assistant_msg} <end>"
        conversations.append(text)

print(f"✅ Laddade {len(conversations)} konversationer")

# Använd ALLA konversationer för träning
print(f"📊 Tränar på ALLA {len(conversations)} konversationer!")

# Skapa dataset
dataset = Dataset.from_dict({"text": conversations})

# Tokenisera
def tokenize_function(examples):
    return tokenizer(
        examples["text"], 
        truncation=True, 
        padding="max_length",
        max_length=128  # Kortare för snabbare träning
    )

print("\n🔤 Tokeniserar data...")
tokenized_dataset = dataset.map(tokenize_function, batched=True)

# Dela i träning och validering
split = tokenized_dataset.train_test_split(test_size=0.1)
train_dataset = split['train']
eval_dataset = split['test']

print(f"📈 Träningsdata: {len(train_dataset)} exempel")
print(f"📉 Valideringsdata: {len(eval_dataset)} exempel")

# Data collator
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False,
)

# Träningsargument - optimerade för alla 26k konversationer
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    overwrite_output_dir=True,
    num_train_epochs=2,  # 2 epoker för 26k data
    per_device_train_batch_size=16,  # Större batch för effektivitet
    per_device_eval_batch_size=16,
    gradient_accumulation_steps=1,
    warmup_steps=500,
    logging_steps=200,
    save_steps=1000,
    eval_strategy="steps",
    eval_steps=1000,
    save_total_limit=2,
    learning_rate=3e-5,
    fp16=torch.cuda.is_available(),
    push_to_hub=False,
    report_to=[],
    load_best_model_at_end=True,
)

# Skapa trainer
trainer = Trainer(
    model=model,
    args=training_args,
    data_collator=data_collator,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
)

print("\n" + "="*60)
print("🎯 STARTAR TRÄNING MED ALLA 26K KONVERSATIONER!")
print("Detta kommer ta cirka 20-30 minuter...")
print("Modellen kommer lära sig creators exakta stil!")
print("="*60 + "\n")

# Träna!
trainer.train()

print("\n💾 Sparar tränad modell...")
trainer.save_model(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

# Spara konfiguration
config = {
    "model_name": MODEL_NAME,
    "training_samples": len(train_dataset),
    "epochs": training_args.num_train_epochs,
    "special_tokens": special_tokens
}

with open(f"{OUTPUT_DIR}/training_config.json", "w") as f:
    json.dump(config, f, indent=2)

print("\n" + "="*60)
print("✅ TRÄNING KLAR!")
print(f"📁 Modell sparad i: {OUTPUT_DIR}")
print("="*60)

# Testa modellen
print("\n🧪 Testar tränad modell...")

def generate_response(prompt, max_length=50):
    input_text = f"<user> {prompt} <assistant>"
    inputs = tokenizer.encode(input_text, return_tensors='pt')
    
    with torch.no_grad():
        outputs = model.generate(
            inputs,
            max_length=inputs.shape[1] + max_length,
            temperature=0.8,
            do_sample=True,
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.encode("<end>")[0]
        )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=False)
    # Extrahera bara assistant-svaret
    if "<assistant>" in response:
        response = response.split("<assistant>")[1]
        if "<end>" in response:
            response = response.split("<end>")[0]
    
    return response.strip()

# Testa med några exempel
test_prompts = [
    "Hey beautiful",
    "What are you doing?",
    "Tell me something hot",
    "I miss you"
]

print("\n📝 Exempel på genererade svar:\n")
for prompt in test_prompts:
    response = generate_response(prompt)
    print(f"User: {prompt}")
    print(f"AI: {response}\n")
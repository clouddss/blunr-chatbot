import json
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer, Trainer, TrainingArguments
from datasets import Dataset
import os

print("\n" + "="*60)
print("🚀 SNABBTRÄNING AV GPT-2 PÅ CREATOR-DATA")
print("="*60)

# Modell och output
MODEL_NAME = "gpt2"
OUTPUT_DIR = "./trained-creator-model"

print("\n1️⃣ Laddar GPT-2...")
tokenizer = GPT2Tokenizer.from_pretrained(MODEL_NAME)
model = GPT2LMHeadModel.from_pretrained(MODEL_NAME)

# Sätt padding token
tokenizer.pad_token = tokenizer.eos_token

print("2️⃣ Laddar träningsdata...")
# Läs träningsdata och formatera för GPT-2
texts = []
with open('training_data.jsonl', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if i >= 5000:  # Begränsa till 5000 för snabb träning
            break
        data = json.loads(line)
        user_msg = data['messages'][0]['content']
        assistant_msg = data['messages'][1]['content']
        
        # Enkel formatering för GPT-2
        text = f"User: {user_msg}\nAssistant: {assistant_msg}\n"
        texts.append(text)

print(f"   Laddat {len(texts)} konversationer")

# Skapa dataset
dataset = Dataset.from_dict({"text": texts})

# Tokenisera
def tokenize_function(examples):
    return tokenizer(examples["text"], truncation=True, padding="max_length", max_length=100)

print("3️⃣ Tokeniserar...")
tokenized_dataset = dataset.map(tokenize_function, batched=True)

# Träningsargument - snabba inställningar
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    overwrite_output_dir=True,
    num_train_epochs=5,  # Fler epoker för bättre inlärning
    per_device_train_batch_size=4,
    save_steps=500,
    save_total_limit=2,
    prediction_loss_only=True,
    learning_rate=5e-5,
    warmup_steps=100,
    logging_steps=50,
    logging_dir='./logs',
)

# Data collator
from transformers import DataCollatorForLanguageModeling
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False,
)

print("4️⃣ Startar träning...")
print("   Detta tar ca 5-10 minuter...")

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    data_collator=data_collator,
    train_dataset=tokenized_dataset,
)

# Träna
trainer.train()

print("\n5️⃣ Sparar modell...")
model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print("\n" + "="*60)
print("✅ TRÄNING KLAR!")
print(f"📁 Modell sparad i: {OUTPUT_DIR}")
print("="*60)
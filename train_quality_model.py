import json
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer, Trainer, TrainingArguments
from datasets import Dataset
from transformers import DataCollatorForLanguageModeling

print("\n" + "="*60)
print("🚀 TRÄNAR GPT-2 PÅ KVALITETSDATA")
print("="*60)

# Konfigurera
MODEL_NAME = "gpt2"
OUTPUT_DIR = "./quality-gpt2-model"

print("\n1️⃣ Laddar GPT-2 modell och tokenizer...")
tokenizer = GPT2Tokenizer.from_pretrained(MODEL_NAME)
model = GPT2LMHeadModel.from_pretrained(MODEL_NAME)

# Sätt padding token
tokenizer.pad_token = tokenizer.eos_token

print("2️⃣ Laddar kvalitetsdata...")
texts = []
with open('quality_training_data.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        texts.append(data['text'])

print(f"   ✅ Laddat {len(texts)} kvalitetskonversationer")

# Skapa dataset
dataset = Dataset.from_dict({"text": texts})

# Tokenisera
def tokenize_function(examples):
    return tokenizer(
        examples["text"], 
        truncation=True, 
        padding="max_length", 
        max_length=128
    )

print("3️⃣ Tokeniserar data...")
tokenized_dataset = dataset.map(tokenize_function, batched=True)

# Dela upp i träning/validering
split = tokenized_dataset.train_test_split(test_size=0.1)
train_dataset = split['train']
eval_dataset = split['test']

print(f"   📊 Träning: {len(train_dataset)} exempel")
print(f"   📉 Validering: {len(eval_dataset)} exempel")

# Data collator
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False,
)

# Träningsargument - optimerade för kvalitet
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    overwrite_output_dir=True,
    num_train_epochs=5,  # Fler epoker för bättre kvalitet
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    warmup_steps=200,
    save_steps=500,
    save_total_limit=2,
    learning_rate=3e-5,
    logging_steps=100,
    eval_strategy="steps",
    eval_steps=500,
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    greater_is_better=False,
)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    data_collator=data_collator,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
)

print("\n4️⃣ STARTAR TRÄNING!")
print("   Detta tar cirka 10-15 minuter...")
print("   Modellen lär sig creator-stil från kvalitetsdata")
print("-" * 60)

# Träna!
trainer.train()

print("\n5️⃣ Sparar tränad modell...")
trainer.save_model(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print("\n" + "="*60)
print("✅ TRÄNING KLAR!")
print(f"📁 Modell sparad i: {OUTPUT_DIR}")
print("🎯 Modellen är tränad på kvalitetskonversationer")
print("="*60)

# Testa modellen direkt
print("\n6️⃣ Testar modellen...")

def generate_response(user_input, max_length=50):
    prompt = f"User: {user_input}\nAssistant:"
    inputs = tokenizer.encode(prompt, return_tensors='pt', max_length=100, truncation=True)
    
    with torch.no_grad():
        outputs = model.generate(
            inputs,
            max_new_tokens=max_length,
            temperature=0.8,
            do_sample=True,
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id,
            repetition_penalty=1.1,
        )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Extrahera bara assistant-svaret
    if "Assistant:" in response:
        response = response.split("Assistant:")[-1].strip()
        # Ta bort eventuell "User:" text
        if "User:" in response:
            response = response.split("User:")[0].strip()
    
    return response

test_inputs = [
    "Hey beautiful",
    "What are you wearing?",
    "Tell me something hot"
]

print("\n📝 Testresultat:\n")
for test in test_inputs:
    response = generate_response(test)
    print(f"User: {test}")
    print(f"AI: {response}\n")
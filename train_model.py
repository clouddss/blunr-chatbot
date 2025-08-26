import json
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from datasets import Dataset
import random

# Använd en svensk/flerspråkig modell som bas
MODEL_NAME = "AI-Sweden-Models/gpt-sw3-356m"  # Svensk GPT-modell från AI Sweden

print(f"Laddar modell: {MODEL_NAME}")

# Ladda tokenizer och modell
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    device_map="auto"
)

# Sätt padding token
tokenizer.pad_token = tokenizer.eos_token

# Läs träningsdata
print("Läser träningsdata...")
training_examples = []
with open('training_data.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        training_examples.append(json.loads(line))

# Formatera data för träning
def format_chat(example):
    user_msg = example['messages'][0]['content']
    assistant_msg = example['messages'][1]['content']
    
    # Ta bort HTML-taggar
    import re
    user_msg = re.sub(r'<[^>]+>', '', user_msg)
    assistant_msg = re.sub(r'<[^>]+>', '', assistant_msg)
    
    # Format för träning
    text = f"Användare: {user_msg}\nAssistent: {assistant_msg}\n"
    return text

# Förbered dataset
print("Förbereder dataset...")
texts = [format_chat(ex) for ex in training_examples[:5000]]  # Begränsa för snabbare träning
dataset = Dataset.from_dict({"text": texts})

# Tokenisera
def tokenize_function(examples):
    return tokenizer(
        examples["text"],
        padding="max_length",
        truncation=True,
        max_length=256
    )

tokenized_dataset = dataset.map(tokenize_function, batched=True)

# Dela upp i träning och validering
split_dataset = tokenized_dataset.train_test_split(test_size=0.1)
train_dataset = split_dataset['train']
eval_dataset = split_dataset['test']

# Träningsargument
training_args = TrainingArguments(
    output_dir="./chatbot-model",
    overwrite_output_dir=True,
    num_train_epochs=3,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    warmup_steps=100,
    logging_steps=50,
    save_steps=500,
    evaluation_strategy="steps",
    eval_steps=500,
    save_total_limit=2,
    learning_rate=5e-5,
    fp16=torch.cuda.is_available(),
    push_to_hub=False,
    report_to=[]
)

# Data collator
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False,
)

# Skapa Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    data_collator=data_collator,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
)

print("Startar träning...")
trainer.train()

print("Sparar modell...")
trainer.save_model("./chatbot-model-final")
tokenizer.save_pretrained("./chatbot-model-final")

print("Träning klar! Modell sparad i ./chatbot-model-final")
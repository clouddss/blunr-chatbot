import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, TaskType, prepare_model_for_kbit_training
from datasets import load_dataset
import json
import os

print("=" * 50)
print("STARTAR LLM-TRÄNING")
print("=" * 50)

# Använd en mindre men effektiv modell som stödjer svenska
MODEL_NAME = "google/gemma-2b"  # Gemma är en effektiv modell som fungerar bra för flerspråkiga uppgifter
# Alternativ: "mistralai/Mistral-7B-Instruct-v0.2" (större men bättre)

print(f"\n1. Laddar modell: {MODEL_NAME}")
print("Detta kan ta några minuter första gången...")

# Ladda tokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)

# Sätt padding token om det inte finns
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"

# Ladda modell med 8-bit kvantisering för att spara minne
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    load_in_8bit=True,
    device_map="auto",
    trust_remote_code=True
)

# Förbered modell för träning
model = prepare_model_for_kbit_training(model)

print("\n2. Konfigurerar LoRA för effektiv finjustering...")
# LoRA-konfiguration för effektiv finjustering
lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=16,  # Rank
    lora_alpha=32,
    lora_dropout=0.1,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],  # För de flesta modeller
)

# Applicera LoRA
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

print("\n3. Laddar träningsdata...")
# Ladda dataset
def load_jsonl(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    return data

train_data = load_jsonl('train_data.jsonl')
val_data = load_jsonl('val_data.jsonl')

print(f"   - Träningsexempel: {len(train_data)}")
print(f"   - Valideringsexempel: {len(val_data)}")

# Konvertera till Hugging Face Dataset
from datasets import Dataset

train_dataset = Dataset.from_list(train_data)
val_dataset = Dataset.from_list(val_data)

# Tokenisera data
def tokenize_function(examples):
    return tokenizer(
        examples["text"],
        truncation=True,
        padding="max_length",
        max_length=256,
    )

print("\n4. Tokeniserar data...")
tokenized_train = train_dataset.map(tokenize_function, batched=True)
tokenized_val = val_dataset.map(tokenize_function, batched=True)

# Data collator
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False,
)

print("\n5. Konfigurerar träning...")
# Träningsargument - optimerade för snabb träning
training_args = TrainingArguments(
    output_dir="./llm-chatbot-model",
    overwrite_output_dir=True,
    num_train_epochs=2,  # Färre epoker för snabbare träning
    per_device_train_batch_size=2,  # Liten batch-storlek för att spara minne
    per_device_eval_batch_size=2,
    gradient_accumulation_steps=4,  # Ackumulera gradienter
    warmup_steps=100,
    logging_steps=100,
    save_steps=500,
    evaluation_strategy="steps",
    eval_steps=500,
    save_total_limit=2,
    learning_rate=2e-4,
    fp16=True,  # Använd mixed precision
    push_to_hub=False,
    report_to=[],
    load_best_model_at_end=True,
)

# Skapa trainer
trainer = Trainer(
    model=model,
    args=training_args,
    data_collator=data_collator,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_val,
)

print("\n6. STARTAR TRÄNING!")
print("=" * 50)
print("Detta kommer ta några minuter...")
print("Modellen lär sig creators kommunikationsstil från datan.")
print("=" * 50)

# Träna modellen
trainer.train()

print("\n7. Sparar tränad modell...")
# Spara modellen
model.save_pretrained("./creator-chatbot-final")
tokenizer.save_pretrained("./creator-chatbot-final")

print("\n✅ TRÄNING KLAR!")
print(f"Modell sparad i: ./creator-chatbot-final")
print("=" * 50)
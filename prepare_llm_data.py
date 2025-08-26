import pandas as pd
import json
import re
from sklearn.model_selection import train_test_split

def clean_html(text):
    """Ta bort HTML-taggar"""
    if pd.isna(text):
        return ""
    text = re.sub(r'<[^>]+>', '', str(text))
    text = text.strip()
    return text

# Läs Excel-filen
print("Läser chattdata...")
df = pd.read_excel("50k chatter hela infloww last 30 days.xlsx")

# Rensa HTML och förbereda data
print("Rensar och förbereder data...")
conversations = []
current_conversation = []
last_user = None

for _, row in df.iterrows():
    fans_msg = clean_html(row['Fans Message'])
    creator_msg = clean_html(row['Creator Message'])
    sent_to = str(row['Sent to']) if pd.notna(row['Sent to']) else "unknown"
    
    # Om vi har en ny användare, spara föregående konversation
    if sent_to != last_user and current_conversation:
        if len(current_conversation) > 1:  # Minst en fråga och ett svar
            conversations.append(current_conversation)
        current_conversation = []
    
    last_user = sent_to
    
    if fans_msg:
        current_conversation.append({"role": "user", "content": fans_msg})
    
    if creator_msg:
        current_conversation.append({"role": "assistant", "content": creator_msg})

# Lägg till sista konversationen
if current_conversation and len(current_conversation) > 1:
    conversations.append(current_conversation)

print(f"Hittade {len(conversations)} konversationer")

# Skapa träningsexempel i chat-format
training_examples = []

for conversation in conversations:
    # Skapa konversationspar
    for i in range(0, len(conversation) - 1, 2):
        if i + 1 < len(conversation):
            if conversation[i]["role"] == "user" and conversation[i+1]["role"] == "assistant":
                # Formatera som en konversation för språkmodellen
                text = f"### Instruktion: Du är en creator som chattar med dina fans. Svara i samma stil som i träningsdata - kort, flirtigt och engagerande.\n\n"
                text += f"### Användare: {conversation[i]['content']}\n\n"
                text += f"### Svar: {conversation[i+1]['content']}"
                
                training_examples.append({
                    "text": text,
                    "user_msg": conversation[i]['content'],
                    "assistant_msg": conversation[i+1]['content']
                })

print(f"Skapade {len(training_examples)} träningsexempel")

# Dela upp i träning och validering
train_data, val_data = train_test_split(training_examples, test_size=0.1, random_state=42)

# Spara träningsdata
with open('train_data.jsonl', 'w', encoding='utf-8') as f:
    for item in train_data:
        f.write(json.dumps({"text": item["text"]}, ensure_ascii=False) + '\n')

with open('val_data.jsonl', 'w', encoding='utf-8') as f:
    for item in val_data:
        f.write(json.dumps({"text": item["text"]}, ensure_ascii=False) + '\n')

# Spara också i format för enklare användning senare
all_creator_responses = [ex["assistant_msg"] for ex in training_examples]
with open('creator_responses.json', 'w', encoding='utf-8') as f:
    json.dump(all_creator_responses, f, ensure_ascii=False, indent=2)

print(f"\nData förberedd:")
print(f"- Träningsdata: {len(train_data)} exempel (train_data.jsonl)")
print(f"- Valideringsdata: {len(val_data)} exempel (val_data.jsonl)")
print(f"- Totalt antal unika creator-svar: {len(set(all_creator_responses))}")

# Visa några exempel
print("\nExempel på träningsdata:")
for i in range(min(3, len(training_examples))):
    print(f"\nExempel {i+1}:")
    print(f"User: {training_examples[i]['user_msg']}")
    print(f"Creator: {training_examples[i]['assistant_msg']}")
import pandas as pd
import json
from collections import defaultdict

# Läs Excel-filen
df = pd.read_excel("50k chatter hela infloww last 30 days.xlsx")

# Gruppera konversationer mellan creator och fans
conversations = defaultdict(list)

for _, row in df.iterrows():
    fans_msg = str(row['Fans Message']) if pd.notna(row['Fans Message']) else None
    creator_msg = str(row['Creator Message']) if pd.notna(row['Creator Message']) else None
    sent_to = str(row['Sent to']) if pd.notna(row['Sent to']) else "unknown"
    
    if fans_msg and fans_msg != 'nan':
        conversations[sent_to].append({
            'role': 'user',
            'content': fans_msg
        })
    
    if creator_msg and creator_msg != 'nan':
        conversations[sent_to].append({
            'role': 'assistant', 
            'content': creator_msg
        })

# Skapa träningsdata i chat-format
training_data = []
creator_messages = []

for user_id, messages in conversations.items():
    # Skapa par av user-assistant meddelanden
    for i in range(len(messages) - 1):
        if messages[i]['role'] == 'user' and i+1 < len(messages) and messages[i+1]['role'] == 'assistant':
            training_data.append({
                'messages': [
                    {'role': 'user', 'content': messages[i]['content']},
                    {'role': 'assistant', 'content': messages[i+1]['content']}
                ]
            })
            creator_messages.append(messages[i+1]['content'])

# Spara träningsdata
with open('training_data.jsonl', 'w', encoding='utf-8') as f:
    for item in training_data:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

# Spara alla creator-meddelanden separat för stilanalys
with open('creator_style.json', 'w', encoding='utf-8') as f:
    json.dump(creator_messages, f, ensure_ascii=False, indent=2)

print(f"Antal träningsexempel: {len(training_data)}")
print(f"Antal unika creator-meddelanden: {len(set(creator_messages))}")
print(f"\nExempel på träningsdata:")
if training_data:
    print(json.dumps(training_data[0], ensure_ascii=False, indent=2))
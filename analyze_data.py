import pandas as pd
import json

# Läs Excel-filen
df = pd.read_excel("50k chatter hela infloww last 30 days.xlsx")

print(f"Antal rader: {len(df)}")
print(f"Kolumner: {df.columns.tolist()}")
print("\nFörsta 5 raderna:")
print(df.head())

# Spara till JSON för enklare hantering
data_for_training = []
for _, row in df.iterrows():
    data_for_training.append({
        'text': str(row.iloc[0]) if not pd.isna(row.iloc[0]) else ""
    })

# Spara till JSON
with open('chat_data.json', 'w', encoding='utf-8') as f:
    json.dump(data_for_training, f, ensure_ascii=False, indent=2)

print(f"\n\nData exporterad till chat_data.json med {len(data_for_training)} meddelanden")
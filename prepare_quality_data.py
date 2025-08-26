import pandas as pd
import json
import re

print("\n" + "="*60)
print("📊 FÖRBEREDER KVALITETSDATA FRÅN TOP CHATTAR")
print("="*60)

# Läs den nya Excel-filen
excel_file = "10k chatter top chattas (2).xlsx"
print(f"\n📂 Läser: {excel_file}")

df = pd.read_excel(excel_file)

print(f"✅ Antal rader: {len(df)}")
print(f"📋 Kolumner: {df.columns.tolist()}")
print("\n📝 Första 3 raderna:")
print(df.head(3))

# Rensa HTML och formatera data
def clean_text(text):
    if pd.isna(text):
        return None
    text = str(text)
    # Ta bort HTML-taggar
    text = re.sub(r'<[^>]+>', '', text)
    text = text.strip()
    return text if text and text != 'nan' else None

# Extrahera konversationer
quality_conversations = []
skipped = 0

for _, row in df.iterrows():
    fans_msg = clean_text(row.get('Fans Message', row.get('Fan Message', '')))
    creator_msg = clean_text(row.get('Creator Message', ''))
    
    # Bara ta med kompletta konversationer
    if fans_msg and creator_msg:
        # Filtrera bort för korta svar
        if len(creator_msg) > 5:
            quality_conversations.append({
                "text": f"User: {fans_msg}\nAssistant: {creator_msg}"
            })
    else:
        skipped += 1

print(f"\n✅ Extraherade {len(quality_conversations)} kvalitetskonversationer")
print(f"⚠️ Hoppade över {skipped} ofullständiga")

# Spara som JSONL för träning
output_file = "quality_training_data.jsonl"
with open(output_file, 'w', encoding='utf-8') as f:
    for conv in quality_conversations:
        json_line = json.dumps(conv, ensure_ascii=False)
        f.write(json_line + '\n')

print(f"💾 Sparade till: {output_file}")

# Visa exempel
print("\n📌 Exempel på träningsdata:")
for i, conv in enumerate(quality_conversations[:3]):
    print(f"\nExempel {i+1}:")
    print(conv['text'])
    print("-" * 40)

print(f"\n✅ Data redo för träning!")
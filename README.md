# AI Chatbot - Creator Style

En AI-chatbot tränad på verkliga chattkonversationer från din Excel-fil.

## Installation

1. Aktivera virtuell miljö:
```bash
source venv/bin/activate
```

2. Installera beroenden (redan gjort):
```bash
pip install pandas openpyxl flask transformers torch datasets
```

## Filer

- `chatbot.py` - Huvudklass för chatbotten med nyckelordsbaserad matchning
- `app.py` - Flask-webbserver
- `prepare_training_data.py` - Förbereder data från Excel
- `training_data.jsonl` - Träningsdata i JSON-format
- `chatbot_model.pkl` - Sparad chatbot-modell
- `templates/chat.html` - HTML-gränssnitt
- `static/css/style.css` - CSS-styling
- `static/js/chat.js` - JavaScript för chattfunktionalitet

## Starta chatbotten

```bash
source venv/bin/activate
python app.py
```

Öppna sedan http://localhost:5000 i din webbläsare.

## Hur det fungerar

1. **Data-analys**: Läser 46,548 chatmeddelanden från Excel-filen
2. **Träning**: Extraherar 25,949 konversationspar (fråga-svar)
3. **Svar-generering**: Använder nyckelordsmatchning för att hitta relevanta svar från creators stil
4. **Webbgränssnitt**: Enkel och snygg chattinterface

## Förbättringar

För bättre prestanda kan du:
- Använda en större svensk språkmodell (kräver mer minne)
- Finjustera GPT-SW3 eller liknande modeller
- Lägga till mer avancerad kontext-hantering
- Implementera sentiment-analys

## Data

Chatbotten är tränad på:
- 25,949 unika konversationspar
- 20,758 unika creator-svar
- 11,922 identifierade nyckelord
# 🎯 Sunriza Chat - LiveKit Agent mit Bithuman Avatar

Ein intelligenter Voice-Agent mit Bithuman Avatar, der über LiveKit kommuniziert und MCP-Tools nutzt.

## ✨ Features

- 🎤 **Voice-Chat** - Natürliche Sprachinteraktion
- 👤 **Bithuman Avatar** - Realistischer Avatar (Hans)
- 🔧 **MCP-Tools** - Zapier-Integration für erweiterte Funktionen
- 🧠 **OpenAI GPT-4** - Intelligente Gespräche
- 🎯 **LiveKit** - Echtzeit-Kommunikation

## 🚀 Quick Start

### 1. Repository klonen
```bash
git clone https://github.com/[dein-username]/sunriza-chat.git
cd sunriza-chat
```

### 2. Virtual Environment einrichten
```bash
cd basic-mcp
python -m venv venv
source venv/bin/activate  # macOS/Linux
# oder
venv\Scripts\activate     # Windows
```

### 3. Dependencies installieren
```bash
pip install -r requirements.txt
```

### 4. Environment Variables setzen
```bash
# .env-Datei erstellen (siehe .env.example)
cp .env.example .env
# API-Keys in .env eintragen
```

### 5. Agent starten
```bash
export $(grep -v "^#" .env | grep -v "^$" | xargs)
python agent.py dev
```

## 🔧 Technische Details

### Problem & Lösung
- **Problem**: `TypeError: cannot pickle '_abc._abc_data' object` mit Python 3.13
- **Lösung**: Manuelle JWT-Erstellung umgeht Pickle-Probleme
- **Dokumentation**: Siehe `basic-mcp/brain.md` für Details

### Architektur
```
basic-mcp/
├── agent.py              # Haupt-Agent mit JWT-Workaround
├── brain.md              # Komplette Dokumentation
├── mcp_client/           # MCP-Integration
├── assets/               # Avatar-Bilder
└── requirements.txt      # Dependencies
```

## 📚 Dokumentation

- **`brain.md`** - Komplette technische Dokumentation
- **JWT-Workaround** - Lösung für Pickle-Probleme
- **Troubleshooting** - Häufige Probleme und Lösungen

## 🎯 Wichtige Hinweise

- **Avatar ist HERZSTÜCK** - Niemals deaktivieren!
- **API-Keys** - Müssen in .env-Datei stehen
- **Python 3.10+** - Empfohlen für Stabilität
- **Code kann "verschwinden"** - Immer prüfen und sichern!

## 🚨 Troubleshooting

### Avatar startet nicht
```bash
# JWT-Code prüfen
grep -n "AccessToken" basic-mcp/agent.py
grep -n "Manual JWT" basic-mcp/agent.py

# Falls nicht da - siehe brain.md für Wiederherstellung
```

### 401-Fehler
- API-Keys in .env prüfen
- Umgebungsvariablen laden: `export $(grep -v "^#" .env | grep -v "^$" | xargs)`

## 📝 License

MIT License - Siehe LICENSE-Datei für Details.

---
*Erstellt: 27.09.2025* 🎯

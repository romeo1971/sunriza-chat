# LiveKit Agent Brain - Bekannte Probleme & Lösungen

## JWT Pickle-Bug (Python 3.13)

### Problem
```
TypeError: cannot pickle '_abc._abc_data' object
```

**Auftritt:** Bei `avatar.start()` mit BitHuman Avatar unter Python 3.13
**Ursache:** Interne JWT-Erstellung von LiveKit/BitHuman verwendet `copy.deepcopy()`, das mit Python 3.13's geänderten ABC-Objekten inkompatibel ist
**Stack:** `bithuman/avatar.py:290` → `access_token.py:188` → `dataclasses.asdict()` → `copy.deepcopy()` → Pickle-Fehler

### Lösung: Manual JWT Workaround

**Code-Location:** `basic-mcp/agent.py` Zeile 18-34 und 123-141

```python
# Manual JWT workaround: Lösung für Pickle-Probleme (Python 3.13)
def generate_livekit_jwt(room: str, identity: str, name: str | None = None) -> str:
    api_key = os.environ.get("LIVEKIT_API_KEY")
    api_secret = os.environ.get("LIVEKIT_API_SECRET")
    if not api_key or not api_secret:
        raise RuntimeError("LIVEKIT_API_KEY/LIVEKIT_API_SECRET nicht gesetzt")

    token = AccessToken(api_key=api_key, api_secret=api_secret)
    token.with_identity(identity)
    if name:
        token.with_name(name)
    token.with_grants(VideoGrants(
        room=room,
        room_join=True,
        can_publish=True,
        can_subscribe=True,
    ))
    return token.to_jwt()

# Anwendung:
manual_jwt = generate_livekit_jwt(room_name, "bithuman-avatar", "BitHuman Avatar Agent")
await avatar.start(session, room=ctx.room, token=manual_jwt)  # ← token-Parameter umgeht internes JWT
```

### Verifizierung
```bash
# JWT-Code prüfen
grep -n "AccessToken" basic-mcp/agent.py
grep -n "Manual JWT" basic-mcp/agent.py

# Erwartete Ausgabe:
# 11:from livekit.api.access_token import AccessToken, VideoGrants
# 18:# Manual JWT workaround: Lösung für Pickle-Probleme (Python 3.13)
# 24:    token = AccessToken(api_key=api_key, api_secret=api_secret)
```

### Status
✅ **Gelöst** - Avatar startet erfolgreich unter Python 3.13 mit manuellem JWT
⚠️ **Temporär** - Sollte in zukünftigen LiveKit/BitHuman Versionen behoben werden

---

## Weitere Probleme

### Deepgram STT Parameter
**Problem:** `STT.__init__() got an unexpected keyword argument 'channels'`
**Lösung:** `channels` nur bei `transcribe()` übergeben, nicht im Konstruktor

### VAD Parameter (LiveKit Agents)
**Problem:** `Agent.__init__() got an unexpected keyword argument 'vad_threshold'`
**Lösung:** VAD-Parameter entfernt, da nicht mehr unterstützt in aktueller Version

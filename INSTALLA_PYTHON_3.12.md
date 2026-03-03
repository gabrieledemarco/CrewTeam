# 🐍 INSTALLA PYTHON 3.12 - Guida Rapida (5 minuti)

## ⚠️ Il Problema
Lo script ha rilevato: **Nessuna versione Python stabile trovata**

Attualmente hai solo Python 3.14 (beta) che non è supportato da CrewAI.

## ✅ La Soluzione: Installa Python 3.12

### PASSO 1: Scarica Python 3.12
1. Vai a: https://www.python.org/downloads/
2. Clicca su **"Python 3.12.x"** (la versione più recente di 3.12)
3. Scorri in basso e scarica: **"Windows installer (64-bit)"**

![download-page]
Cerca questa sezione sulla pagina:
┌─────────────────────────────────────────┐
│ Stable Releases                         │
├─────────────────────────────────────────┤
│ Python 3.12.x                           │
│ └─ Windows installer (64-bit) ← SCARICA │
│                                         │
│ Python 3.11.x                           │
│ Python 3.10.x                           │
└─────────────────────────────────────────┘

### PASSO 2: Esegui l'Installatore
1. Vai alla cartella **Download**
2. Doppio click su: `python-3.12.x-amd64.exe`
3. Attendi che si apra la finestra di installazione

### PASSO 3: Configurazione CRITICA
Quando vedi questa schermata:

```
┌─────────────────────────────────────────────────┐
│ Python 3.12.x Setup                             │
├─────────────────────────────────────────────────┤
│                                                 │
│  ☐ Install launcher for all users              │
│  ☐ Add Python 3.12 to PATH  ← ☑ SPUNTA QUESTO! │
│                                                 │
│     [Install Now]     [Customize Installation] │
│                                                 │
└─────────────────────────────────────────────────┘
```

**IMPORTANTE**: Spunta la casella "Add Python 3.12 to PATH" (quella con il checkmark ☑)

Poi clicca: **"Install Now"**

### PASSO 4: Attendi Installazione
La finestra mostrerà:
```
Installing Python 3.12.x...
[████████████████████] 100%
Setup was successful
```

Clicca: **"Close"** o **"Next"**

### PASSO 5: Riavvia il Computer
⚠️ **IMPORTANTE**: Riavvia il computer affinché il PATH sia aggiornato

```
Start Menu → Alimentazione → Riavvia
```

---

## ✅ Verifica Installazione

Dopo il riavvio, apri **PowerShell** o **CMD** e verifica:

```powershell
py -3.12 --version
```

Dovresti vedere:
```
Python 3.12.x
```

Se vedi questo, significa che Python 3.12 è installato correttamente! ✅

---

## 🎯 Dopo l'Installazione

Una volta verificato Python 3.12, torna a CREW e esegui:

```powershell
cd C:\Users\gabri\Desktop\CREW
.\SETUP_FIX.bat
```

Questa volta lo script **troverà Python 3.12** e risolverà tutto automaticamente! 🚀

---

## 🆘 Se Non Funziona

### Errore: "py: command not found"
Significa che il PATH non è aggiornato
1. Riavvia il computer (se non l'hai già fatto)
2. Ricerca "Variabili d'ambiente" in Windows
3. Clicca: "Modifica le variabili d'ambiente di sistema"
4. Clicca: "Variabili d'ambiente..."
5. Nella sezione "Variabili di sistema", verifica che il PATH contenga `C:\Users\[username]\AppData\Local\Programs\Python\Python312`

### Errore: "Python 3.12 not found"
1. Verifica di aver spuntato "Add Python to PATH" durante l'installazione
2. Riavvia il computer
3. Se persiste, disinstalla e reinstalla Python 3.12

### Script Batch ancora non lo trova
1. Apri PowerShell
2. Esegui manualmente:
   ```powershell
   py -3.12 --version
   ```
3. Se funziona, ma lo script non lo trova, è un problema di PATH
   - Riavvia definitivamente il computer
   - Prova di nuovo

---

## ⏱️ Tempistiche
- Scarica: 2-3 minuti (dipende da connessione)
- Installazione: 2-3 minuti
- Riavvio computer: 1-2 minuti
- **Totale: ~5-8 minuti**

---

## 📊 Versioni Python Supportate

| Versione | Status | Supportata |
|----------|--------|-----------|
| 3.14 (attuale) | Beta | ❌ NO |
| 3.13 | Stabile | ✅ Sì |
| **3.12** | Stabile | ✅ **CONSIGLIATO** |
| 3.11 | Stabile | ✅ Sì |
| 3.10 | Legacy | ✅ Sì |

---

## 🎓 Perché 3.12?
- ✅ Completamente stabile
- ✅ Tutte le dipendenze hanno wheel pre-compilate
- ✅ Supportato da CrewAI, LangChain, LiteLLM
- ✅ Più veloce di 3.14 beta
- ✅ Compatibile con tutti gli strumenti

---

## ✨ Il Prossimo Passo

1. **Installa Python 3.12** (seguendo questa guida)
2. **Riavvia il computer**
3. **Verifica**: `py -3.12 --version`
4. **Esegui**: `.\SETUP_FIX.bat` dalla cartella CREW
5. **Fine!** ✅

---

**Tempo totale: ~15-20 minuti per installare + riavviare + correggere**

Poi avrai un ambiente completamente funzionante! 🚀

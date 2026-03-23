# 🧠 ElderCare AI — MVP

**Early Cognitive Decline Detection via Daily Voice & Chat Interaction**

> ⚠️ This is a **screening aid only**, not a medical diagnostic tool. All results must be reviewed by a qualified physician.

---

## What This Is

ElderCare AI is a web-based MVP that lets elderly users (or their caregivers) have natural daily conversations — either by typing or uploading a voice recording — while the AI analyzes linguistic markers associated with early cognitive decline.

**Research basis:**
- Lima et al. (2025) — *Evaluating spoken language as a biomarker for automated screening of cognitive impairment*, Communications Medicine / Nature
- PMC12714990 / Frontiers in Aging Neuroscience (2025) — *Enhancing dementia detection with LLMs and speech representation learning*

**Linguistic markers analyzed:**
| Marker | What it detects |
|---|---|
| Type-Token Ratio (TTR) | Lexical diversity — MCI patients show lower TTR |
| Phrase repetition rate | Repeated bigrams — strong MCI indicator |
| Avg. sentence length | Simplified syntax — associated with cognitive decline |
| Topic coherence | Discourse coherence reduction — MCI marker |

**Risk thresholds (conservative):**
| Score | Risk Level |
|---|---|
| 0 – 39 | 🟢 Low |
| 40 – 64 | 🟡 Moderate |
| 65 – 100 | 🔴 High |

---

## Features

- 💬 **Chat tab** — Daily conversational AI, warm & natural
- 🎙️ **Voice tab** — Upload audio → auto-transcribe → analyze
- 📊 **Dashboard tab** — Composite risk score, marker breakdown, session history

---

## Quick Start (Local)

### 1. Clone / download the project
```bash
git clone <your-repo>
cd eldercare-ai
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set API keys

Create `.streamlit/secrets.toml`:
```toml
ANTHROPIC_API_KEY = "sk-ant-..."   # https://console.anthropic.com
GROQ_API_KEY = "gsk_..."           # https://console.groq.com  (FREE)
```

### 5. Run
```bash
streamlit run app.py
```

Open http://localhost:8501 — done!

---

## Deploy to Streamlit Cloud (Free, Public URL)

This is the recommended way to share with judges — **no installation needed** for users.

### Step 1 — Push to GitHub
```bash
git init
git add .
git commit -m "ElderCare AI MVP"
git remote add origin https://github.com/YOUR_USERNAME/eldercare-ai.git
git push -u origin main
```

### Step 2 — Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **"New app"**
4. Select your repo → branch `main` → main file `app.py`
5. Click **"Advanced settings"** → **"Secrets"** and paste:
   ```
   ANTHROPIC_API_KEY = "sk-ant-..."
   GROQ_API_KEY = "gsk_..."
   ```
6. Click **Deploy** — your app will be live at `https://YOUR_USERNAME-eldercare-ai-app-XXXX.streamlit.app`

**That's it. Share the URL with judges — they open browser, no install.**

---

## API Keys — Where to Get Them

| Key | Source | Cost |
|---|---|---|
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) | Pay-as-you-go (tiny usage for MVP) |
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) | **Free tier available** |

**The app works without keys** — chat uses fallback replies, voice transcription shows an error message. For full functionality, both keys are needed.

---

## Project Structure

```
eldercare-ai/
├── app.py                    # Main Streamlit UI
├── cognitive_analyzer.py     # NLP analysis engine (research-based)
├── session_manager.py        # In-session data management
├── requirements.txt
└── .streamlit/
    ├── config.toml           # Theme & server config
    └── secrets.toml.example  # Key template (DO NOT commit actual keys)
```

---

## Roadmap

| Phase | Timeline | Goal |
|---|---|---|
| Alpha (this) | Year 1 | Web MVP, text + voice, 30 users |
| Beta | Year 3 | Mobile app, 500 users, 10 Puskesmas |
| Scale | Year 5 | 10,000+ elderly monitored, ASEAN expansion |

---

## Citation

Lima, M. R., et al. (2025). Evaluating spoken language as a biomarker for automated screening of cognitive impairment. *Communications Medicine, Nature*. https://doi.org/10.5281/zenodo.17370485

PMC12714990 — Frontiers in Aging Neuroscience (2025). Enhancing dementia and cognitive decline detection with LLMs and speech representation learning.

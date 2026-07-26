# AI Operations Copilot

**Agentic AI for industrial asset monitoring** — ask plain-English questions about plant equipment; the system intelligently selects the right tools and returns clear, actionable recommendations.

> Portfolio project targeting AI Engineering roles in Oil & Gas, Energy, and Heavy Industry.

---

## Overview

Traditional predictive maintenance systems answer single, narrow questions. Real operational decisions require **cross-checking** multiple data sources — sensor readings, failure probabilities, and historical maintenance logs.

The AI Operations Copilot mimics this reasoning process. It uses an **agentic architecture** that:

1. **Understands** your natural language question  
2. **Selects** the appropriate tools (sensor analysis, failure risk, document search)  
3. **Synthesizes** results into a single, readable recommendation  

**Demo assets:** `P-104` (pump), `C-7` (compressor), `P-22` (pump), `T-12` (tank)

---

## Architecture

```text
User Question
      ↓
┌─────────────────────────────────────────────────────────────┐
│  Agent (Claude via Bedrock / Anthropic API / Fallback)      │
│  • Understands intent                                       │
│  • Selects which tools to call                              │
│  • Synthesizes results                                      │
└─────────────────────────────────────────────────────────────┘
      ↓                    ↓                    ↓
┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐
│ Sensor      │    │ Failure     │    │ Document            │
│ Check       │    │ Risk        │    │ Search              │
│ Isolation-  │    │ Random      │    │ Semantic /          │
│ Forest      │    │ Forest      │    │ TF-IDF              │
└─────────────┘    └─────────────┘    └─────────────────────┘
      ↓                    ↓                    ↓
┌─────────────────────────────────────────────────────────────┐
│                   Synthesised Answer                        │
└─────────────────────────────────────────────────────────────┘
```

| Tool | Question it answers |
|------|---------------------|
| **Sensor check** | Do current readings look unusual? (IsolationForest) |
| **Failure risk** | How likely is failure? (Random Forest on [AI4I 2020](https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset)) |
| **Document search** | What do past maintenance logs show? (semantic / TF-IDF search) |

---

## Project structure

```text
agent/
├── copilot.py                 # Agent: tool selection + answer synthesis

tools/
├── sensor_tool.py             # Live-style sensor anomaly check
├── failure_risk_tool.py       # Failure probability (AI4I-trained model)
├── document_search_tool.py    # Maintenance log search

data/                          # Asset DB, logs, trained classifier

api.py                         # FastAPI: POST /ask, GET /health
frontend/                      # React + Vite chat UI (premium local demo)
streamlit_app.py               # Public Streamlit demo (safe to share)
main.py                        # Command-line chat

scripts/
├── train_failure_model.py     # Train / refresh failure classifier

SETUP_AWS_BEDROCK.md           # AWS Bedrock (Claude) setup guide
requirements.txt               # Full / local dependencies
requirements-demo.txt          # Streamlit demo dependencies
```

---

## Operating modes

| Mode | LLM provider | Best for |
|------|--------------|----------|
| **Public demo** | No LLM (fallback) | Sharing a public Streamlit link — no AWS cost |
| **Real agent** | AWS Bedrock or Anthropic API | Interviews, local portfolio demos |
| **Fallback** | No LLM | Offline / keyword-based tool selection |

> **Note:** Fallback mode uses keyword matching to select tools. It may miss nuanced phrasing (e.g. “has it had issues before?” without the word *history*). The real Claude agent understands meaning and selects tools correctly.

AWS Bedrock setup: **[SETUP_AWS_BEDROCK.md](SETUP_AWS_BEDROCK.md)**

---

## Quick start

### Prerequisites

- Python 3.10+
- (Optional) AWS CLI configured for Bedrock access  
- (Optional) Anthropic API key  
- (Optional) Node.js 18+ for the React UI  

### One-time setup

```bash
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
python scripts/train_failure_model.py
```

### Optional — better document search

```bash
pip install sentence-transformers
```

---

## Ways to run

### 1. Public Streamlit demo (recommended for sharing)

Safe for GitHub + [Streamlit Community Cloud](https://share.streamlit.io). **No AWS keys. No Bedrock cost.**

```bash
pip install -r requirements-demo.txt
streamlit run streamlit_app.py
```

**Deploy to Streamlit Cloud:**

1. Push the repo to GitHub (**never** commit `.env` or AWS keys)  
2. Create an app at Streamlit Cloud  
3. Main file: `streamlit_app.py`  
4. Dependencies: `requirements-demo.txt`  
5. Do **not** add AWS secrets for public deployment  

---

### 2. Premium React UI + FastAPI (local / interviews)

Best-looking demo — ideal for portfolio presentations.

**Terminal 1 — API** (port `8002`):

```bash
uvicorn api:app --reload --port 8002
```

**Terminal 2 — UI:**

```bash
cd frontend
npm install
npm run dev
```

Open: [http://localhost:5173](http://localhost:5173)

If you change the API port, update `VITE_API_BASE_URL` in `frontend/.env`.

---

### 3. Command-line chat

```bash
python main.py
```

---

### 4. Enable real Claude agent (local)

**Option A — Amazon Bedrock** (uses AWS credits):

```bash
# Follow SETUP_AWS_BEDROCK.md, then:
aws configure

# Windows PowerShell
$env:USE_BEDROCK = "1"

# macOS / Linux
export USE_BEDROCK=1
```

**Option B — Anthropic direct API:**

```bash
# Windows PowerShell
$env:ANTHROPIC_API_KEY = "your-key-here"
$env:USE_BEDROCK = "0"

# macOS / Linux
export ANTHROPIC_API_KEY="your-key-here"
export USE_BEDROCK=0
```

Without credentials, the app runs in **fallback** mode.

---

## Example questions

| Question |
|----------|
| How is pump P-104 doing? |
| What's the failure risk for compressor C-7? |
| Has there been any corrosion reported on tanks? |
| Check P-22 and tell me if there's any related maintenance history |
| What is the current vibration on P-104? |

---

## Technology stack

| Layer | Technology |
|-------|------------|
| Agent | Claude tool-calling (AWS Bedrock / Anthropic API) |
| ML models | scikit-learn — IsolationForest, Random Forest |
| Search | sentence-transformers (optional) / TF-IDF fallback |
| Backend API | FastAPI + Uvicorn |
| Frontend | React + Vite (premium UI) |
| Public demo | Streamlit |
| Data | AI4I 2020 Predictive Maintenance Dataset |

---

## Limitations

| Limitation | Explanation |
|------------|-------------|
| Fallback ≠ real agent | Keyword rules miss some natural phrasings; Claude handles nuanced intent correctly. |
| Simulated sensor data | Asset data is generated for demos; production would integrate with historian/SCADA feeds. |
| Search quality | Without `sentence-transformers`, TF-IDF is weaker (e.g. “leak” vs “drip”). |

---

## Security note

| Do | Don’t |
|----|--------|
| Deploy Streamlit in demo mode | Commit AWS access keys or `.env` files |
| Keep Bedrock for local / private demos | Expose unrestricted Bedrock on public URLs |
| Use environment variables for credentials | Hardcode credentials in source code |

---

## Roadmap

- [ ] Integrate real historian / SCADA telemetry  
- [ ] Add OT/ICS security context as a fourth tool  
- [ ] Host React UI with locked-down private API  
- [ ] Add multi-asset batch analysis  
- [ ] Implement alerting and notification system  

---

## License

This project is a portfolio demonstration. All outputs are **assistive only** — maintenance and safety decisions must be confirmed by qualified engineers.

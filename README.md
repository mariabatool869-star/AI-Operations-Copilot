# AI Operations Copilot

**Agentic AI for industrial asset monitoring** — ask plain-English questions about plant equipment; the system chooses the right tools, then returns a clear recommendation.

> Portfolio project for Oil & Gas, energy, and heavy-industry AI roles.

---

## What it does

You ask things like *“How is pump P-104 doing?”* The copilot can:

| Tool | Question it answers |
|------|---------------------|
| **Sensor check** | Do current readings look unusual? (IsolationForest) |
| **Failure risk** | How likely is failure? (Random Forest on [AI4I 2020](https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset)) |
| **Maintenance search** | What showed up in past logs? (semantic / TF-IDF search) |

It then combines those results into one readable answer — similar to how an engineer checks several sources instead of following a single fixed script.

**Demo assets:** `P-104` (pump), `C-7` (compressor), `P-22` (pump), `T-12` (tank)

---

## Why this architecture

Single models (anomaly detection *or* failure prediction) each answer one narrow question. Real judgment needs **cross-checking**. This project wraps proven detection logic in an **agent** that decides *which* tools to call for each question.

---

## Project layout

```text
agent/copilot.py               Agent: tool selection + answer synthesis
tools/sensor_tool.py           Live-style sensor anomaly check
tools/failure_risk_tool.py     Failure probability (AI4I-trained model)
tools/document_search_tool.py  Maintenance log search
data/                          Asset DB, logs, trained classifier
api.py                         FastAPI: POST /ask, GET /health
frontend/                      React + Vite chat UI (premium local demo)
streamlit_app.py               Public Streamlit demo (safe to share)
main.py                        Command-line chat
scripts/train_failure_model.py Train / refresh the failure classifier
SETUP_AWS_BEDROCK.md           AWS Bedrock (Claude) setup guide
```

---

## Operating modes

| Mode | When | Uses cloud LLM? | Best for |
|------|------|-----------------|----------|
| **Public demo** | `DEMO_MODE=1` (Streamlit app sets this) | No | Sharing a public link — **no AWS cost** |
| **Real agent** | AWS Bedrock or `ANTHROPIC_API_KEY` | Yes (Claude tool-calling) | Interviews, local portfolio demos |
| **Fallback** | No credentials (or demo mode) | No | Offline / keyword-based tool selection |

**Honest note:** Fallback picks tools with keywords. It can miss intent (e.g. *“has it had issues before?”* without the word *history*). The real Claude agent understands meaning and chooses tools correctly.

AWS setup for real mode: **[SETUP_AWS_BEDROCK.md](SETUP_AWS_BEDROCK.md)**

---

## Quick start (one-time setup)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts\train_failure_model.py
```

Optional (better log search):

```powershell
pip install sentence-transformers
```

---

## Ways to run

### 1. Public Streamlit demo (recommended to share)

Safe for GitHub + [Streamlit Community Cloud](https://share.streamlit.io). **No AWS keys. No Bedrock spend.**

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements-demo.txt
streamlit run streamlit_app.py
```

**Deploy:**

1. Push the repo to GitHub (never commit `.env` or AWS keys).
2. Create an app at Streamlit Cloud → main file: `streamlit_app.py`.
3. Use dependency file: `requirements-demo.txt`.
4. Do **not** add AWS secrets for the public app.

---

### 2. Premium React UI + FastAPI (local / interviews)

Best-looking demo when you have Bedrock configured.

**Terminal 1 — API** (default port **8002**):

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn api:app --reload --port 8002
```

**Terminal 2 — UI:**

```powershell
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

If you change the API port, update `VITE_API_BASE_URL` in `frontend/.env` to match.

---

### 3. Command-line chat

```powershell
.\.venv\Scripts\Activate.ps1
python main.py
```

---

### Enable the real Claude agent (local)

Prefer **Amazon Bedrock** (uses your AWS credits): follow [SETUP_AWS_BEDROCK.md](SETUP_AWS_BEDROCK.md), then:

```powershell
aws configure
```

Or use Anthropic directly:

```powershell
$env:ANTHROPIC_API_KEY = "your-key-here"
$env:USE_BEDROCK = "0"
```

Without credentials, the app still runs in **fallback** mode.

---

## Example questions

- How is pump P-104 doing?
- What's the failure risk for compressor C-7?
- Has there been any corrosion reported on tanks?
- Check P-22 and tell me if there's any related maintenance history
- What is the current vibration on P-104?

---

## Tech stack

- **Agent:** Claude tool-calling via Amazon Bedrock or Anthropic API  
- **ML:** scikit-learn — IsolationForest, Random Forest (AI4I 2020)  
- **Search:** sentence-transformers (optional) or TF-IDF fallback  
- **APIs / UI:** FastAPI, React + Vite, Streamlit  

---

## Limitations (documented honestly)

1. **Fallback ≠ real agent** — keyword rules miss some natural phrasings; Claude does not.  
2. **Sensor / asset data are simulated** — suitable for demos; production would use historian/SCADA feeds. Failure risk uses a **real** published dataset.  
3. **Search quality** — without `sentence-transformers`, TF-IDF is weaker (e.g. “leak” vs “drip”).  

---

## Security note for public demos

| Do | Don’t |
|----|--------|
| Deploy Streamlit in demo mode | Commit AWS access keys or `.env` |
| Keep Bedrock for local / private demos | Expose unrestricted Bedrock on a public URL |

---

## Possible next steps

- Connect real historian / SCADA telemetry  
- Add OT/ICS security context as a fourth tool  
- Host the React UI with a locked-down private API for invite-only demos  

---

## License / use

Built as a portfolio demonstration. Outputs are **assistive only** — maintenance and safety decisions must be confirmed by a qualified engineer.

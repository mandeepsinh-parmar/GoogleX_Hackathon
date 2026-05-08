# Context Handoff: Startup India Advisor → GoogleX_Hackathon

> Paste this entire document into your new chat to give the AI full context.

---

## Project Summary

This is a **Flask-based web application** called **Startup India Advisor** (now living in the `GoogleX_Hackathon` folder). It provides AI-powered location intelligence and government scheme matching to help entrepreneurs pick the best Indian state to start their business.

---

## Current Project State

- ✅ Flask app is working and runs successfully
- ✅ Analysis engine (state ranking, scheme matching, subsidy estimation) is fully functional
- ✅ Google Gemini chat endpoint is live and working
- ✅ `.gitignore`, `.env.example`, and `README.md` have been created for proper repo hygiene
- ⚠️ Google Maps is NOT loading — see details below
- ⚠️ ADK (Google Agent Development Kit) is disabled — see details below

---

## Tech Stack

- **Backend:** Python + Flask
- **AI:** Google Gemini via `google-generativeai` package
- **Maps:** Google Maps JavaScript API (front-end only)
- **Data:** Static JSON files in `data/` folder
- **Virtual env:** `.venv` (Python)

---

## Folder Structure

```
GoogleX_Hackathon/   (was: startup_india_advisor/)
├── app.py                    # Main Flask app
├── requirements.txt          # Dependencies (google-adk is commented out)
├── .env                      # Real API keys (DO NOT commit)
├── .env.example              # Safe template (committed to git)
├── .gitignore                # Hides .env, .venv, __pycache__, etc.
├── README.md                 # Project documentation
├── data/
│   ├── state_scores.json     # Static infrastructure scores for 8 states
│   ├── schemes.json          # Central + state government schemes database
│   └── industrial_parks.json # Industrial park listings
├── tools/
│   ├── location_tools.py     # Search parks, get infra scores, geocode
│   ├── scheme_tools.py       # Match schemes, estimate subsidies
│   └── scoring_tools.py      # Weighted multi-criteria scoring engine
└── templates/
    └── index.html            # Full frontend UI with Google Maps
```

---

## Environment Variables (`.env`)

```
GOOGLE_API_KEY=<gemini key from aistudio.google.com>
GOOGLE_MAPS_API_KEY=<maps key from cloud.google.com>
```

> ✅ The old repo was deleted. A fresh repo was created with `.gitignore` already in place — keys are safe.

---

## How to Run

```bash
cd GoogleX_Hackathon
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
python app.py
# Open http://127.0.0.1:5000
```

---

## Known Issues & Their Status

### 1. 🗺️ Google Maps Not Loading (`ApiTargetBlockedMapError`)

**Root Cause:** The Google Maps API Key has an **"API restriction"** applied to it. It was restricted to only the **Solar API**, blocking the Maps JavaScript API.

**Fix (user still needs to complete):**
1. Go to [Google Cloud Credentials](https://console.cloud.google.com/apis/credentials)
2. Click on the Maps API key
3. Scroll to "API restrictions" → open the dropdown
4. Check **"Maps JavaScript API"** → click OK → click **Save**
5. Wait 2 minutes → refresh the app

The project has billing enabled (`Google Cloud Platform Trial Billing Account` linked to `startupadvisor-495706`), so billing is NOT the issue.

---

### 2. 🤖 ADK (Agent Development Kit) Disabled

**Root Cause:** `google-adk` caused an infinite dependency resolution loop during `pip install`. It was commented out in `requirements.txt`.

**Current behavior:** The `/api/analyze` endpoint returns a 503 error. All other endpoints (rank-states, schemes, parks, subsidy, chat) work perfectly as they use direct tool calls.

**Fix (if needed):** Try installing ADK in isolation and check for version conflicts with the existing `google-generativeai` package.

---

### 3. 📊 Analysis Data is Static (Not Real-Time)

The "AI analysis" is not pulling live data. Here's how it actually works:

- `data/state_scores.json` has hardcoded metrics for **exactly 8 states**: Gujarat, Karnataka, Tamil Nadu, Maharashtra, Telangana, Uttar Pradesh, Rajasthan, Andhra Pradesh
- `tools/scoring_tools.py` multiplies those static numbers by user-selected priority weights to produce scores
- Scheme matching reads from `data/schemes.json` (static list of schemes)
- The Gemini AI is only used in the `/api/chat` chatbot endpoint

This is a **prototype/demo** — not connected to live government data sources.

---

## Key Bug Fixes Applied in Previous Session

1. **`requirements.txt`** — Commented out `google-adk` to prevent infinite pip loop
2. **`app.py` line 283** — Fixed `SyntaxError: unexpected character after line continuation character` caused by escaped triple-quotes in f-string (`\"\"\"` → `"""`)
3. **`app.py` imports** — Changed absolute imports (`from startup_india_advisor.tools...`) to relative imports (`from tools...`) so the script runs correctly from the project root
4. **`.venv` rebuild** — The virtual environment was corrupted (missing `pyvenv.cfg`). Was deleted and recreated from scratch

---

## API Endpoints Reference

| Method | Endpoint | Status | Description |
|--------|----------|--------|-------------|
| GET | `/` | ✅ Working | Main UI |
| POST | `/api/rank-states` | ✅ Working | Rank all 8 states by business profile |
| POST | `/api/schemes` | ✅ Working | Match government schemes |
| POST | `/api/parks` | ✅ Working | Search industrial parks |
| POST | `/api/subsidy` | ✅ Working | Estimate subsidy value |
| POST | `/api/chat` | ✅ Working | Gemini AI Q&A |
| POST | `/api/infrastructure` | ✅ Working | Get state infra score |
| POST | `/api/geocode` | ✅ Working | Geocode an address |
| POST | `/api/analyze` | ❌ 503 | Full ADK agent chain (disabled) |
| GET | `/api/health` | ✅ Working | Health check |

---

## Git Hygiene Checklist

- [x] `.gitignore` created (hides `.env`, `.venv/`, `__pycache__/`, etc.)
- [x] `.env.example` exists with placeholder values
- [x] `README.md` created with full setup instructions
- [x] Old repo deleted — fresh repo created with `.gitignore` already in place (keys never exposed)

---

## Next Steps / Open Tasks

1. **Fix Google Maps** — Add "Maps JavaScript API" to the key's API restrictions in Cloud Console
3. **Expand state coverage** — Currently only 8 Indian states are supported; adding more requires updating `data/state_scores.json` and `data/schemes.json`
4. **Real data integration** — Replace static JSON with live APIs (e.g., data.gov.in, Startup India portal)
5. **Re-enable ADK** — Resolve version conflicts to enable the full agent chain at `/api/analyze`

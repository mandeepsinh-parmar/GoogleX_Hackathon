# Startup India Advisor 🚀

AI-powered location intelligence and government scheme matching for businesses in India.

## Overview

This tool helps entrepreneurs and investors identify the best Indian states to set up their business by:
- Ranking states using weighted multi-criteria scoring
- Matching applicable central and state government schemes
- Estimating subsidy values
- Providing AI-powered Q&A via Google Gemini

## Tech Stack

- **Backend:** Python + Flask
- **AI:** Google Gemini (`google-generativeai`)
- **Maps:** Google Maps JavaScript API
- **Data:** Static JSON datasets (`data/`)

## Setup

### 1. Clone the repo
```bash
git clone <your-repo-url>
cd startup_india_advisor
```

### 2. Create a virtual environment
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Keys
Copy the example environment file and fill in your keys:
```bash
cp .env.example .env
```

Edit `.env`:
```
GOOGLE_API_KEY=your_gemini_api_key_from_aistudio.google.com
GOOGLE_MAPS_API_KEY=your_maps_key_from_cloud.google.com
```

> ⚠️ **Never commit your `.env` file.** It is already in `.gitignore`.

### 5. Run the app
```bash
python app.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Main UI |
| POST | `/api/rank-states` | Rank all states for a business profile |
| POST | `/api/schemes` | Match government schemes |
| POST | `/api/parks` | Search industrial parks |
| POST | `/api/subsidy` | Estimate subsidy value |
| POST | `/api/chat` | AI Q&A via Gemini |
| GET | `/api/health` | Health check |

## Project Structure

```
startup_india_advisor/
├── app.py                  # Flask application
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── .gitignore              # Git ignore rules
├── data/
│   ├── state_scores.json   # State infrastructure metrics
│   ├── schemes.json        # Government scheme database
│   └── industrial_parks.json
├── tools/
│   ├── location_tools.py   # Location intelligence
│   ├── scheme_tools.py     # Scheme matching
│   └── scoring_tools.py    # Weighted scoring engine
└── templates/
    └── index.html          # Frontend UI
```

## License

MIT

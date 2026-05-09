# 🏗️ Architecture — Multi-Agent Industrial Geolocation Engine

## System Overview

The platform uses a **multi-agent architecture** where three specialized AI agents work in sequence, orchestrated by a Flask backend via Server-Sent Events (SSE) for real-time progress streaming to the frontend.

---

## Full System Architecture

```mermaid
flowchart TB
    subgraph USER["👤 User Interface"]
        UI["Web App<br/>(Flask + Google Maps)"]
        WIZARD["Search Wizard<br/>Sector / State / Land / Budget"]
    end

    subgraph BACKEND["⚙️ Flask Backend (app.py)"]
        direction TB
        API_FIND["/api/find-parks"]
        API_PIPE["/api/run-pipeline<br/>(SSE Stream)"]
        API_REC["/api/ai-recommendation"]
        API_ROI["/api/roi-calculator"]
        API_PDF["/api/export/pdf"]
        API_XLS["/api/export/excel"]
    end

    subgraph PIPELINE["🔄 Multi-Agent Pipeline (Steps 2→7)"]
        direction TB

        STEP2["Step 2: Query Engine<br/>Filter iilb_parks.json<br/>(4200+ parks)"]

        subgraph AGENT1["🤖 Agent 1 — Scraper Agent"]
            S3A["Geocode Park<br/>(Find Place → Place Details)"]
            S3B["Fetch Logistics<br/>(Places + Distance Matrix)"]
            S3C["Gemini Research<br/>Water / Raw Materials / Incentives"]
        end

        STEP4["Step 4: Store to MongoDB"]

        subgraph AGENT2["🤖 Agent 2 — Ranking Agent"]
            S5A["Phase A: Multi-Criteria Scoring<br/>Sector(20) + Land(20) + Logistics(20)<br/>+ Water(10) + Incentives(15)<br/>+ Plug&Play(5) + RawMats(10)"]
            S5B["Phase B: Deep Research<br/>Gemini AI analysis on Top 10"]
        end

        subgraph AGENT3["🤖 Agent 3 — Scheme Agent"]
            S6A["Gemini + Google Search Grounding"]
            S6B["Central Schemes Lookup"]
            S6C["State Schemes Lookup"]
            S6D["Subsidy Stack Estimation"]
        end

        STEP7["Step 7: Final Results<br/>Top 10 Ranked Parks"]
    end

    subgraph TOOLS["🧰 Tool Modules"]
        T_LOC["location_tools.py<br/>query_parks / geocode"]
        T_SCH["scheme_tools.py<br/>match_government_schemes"]
        T_SCORE["scoring_tools.py<br/>calculate_location_score"]
        T_EXPORT["export_tools.py<br/>PDF + Excel generation"]
    end

    subgraph EXTERNAL["☁️ External APIs"]
        GMAPS["Google Maps Platform<br/>Geocoding + Places +<br/>Distance Matrix"]
        GEMINI["Google Gemini API<br/>(v1beta REST)<br/>gemini-2.0-flash"]
        GSEARCH["Google Search<br/>Grounding<br/>(via Gemini)"]
    end

    subgraph DATA["💾 Data Layer"]
        JSON["iilb_parks.json<br/>4200+ Industrial Parks"]
        MONGO["MongoDB<br/>scraped_parks +<br/>analysis_sessions"]
        CACHE["In-Memory Cache<br/>(Fallback)"]
    end

    subgraph POST_PIPELINE["📊 Post-Pipeline Features"]
        AI_REC["Live AI Recommendation"]
        ROI["ROI Calculator"]
        PDF_GEN["PDF Report Generator"]
        XLS_GEN["Excel Export"]
    end

    %% User Flow
    WIZARD --> API_FIND
    API_FIND --> STEP2
    STEP2 --> API_PIPE

    %% Pipeline Flow
    API_PIPE --> AGENT1
    S3A --> S3B --> S3C
    AGENT1 --> STEP4
    STEP4 --> AGENT2
    S5A --> S5B
    AGENT2 --> AGENT3
    S6A --> S6B
    S6A --> S6C
    S6B --> S6D
    S6C --> S6D
    AGENT3 --> STEP7
    STEP7 --> UI

    %% Post-pipeline
    UI --> API_REC --> AI_REC
    UI --> API_ROI --> ROI
    UI --> API_PDF --> PDF_GEN
    UI --> API_XLS --> XLS_GEN

    %% Tool connections
    STEP2 -.- T_LOC
    AGENT2 -.- T_SCORE
    AGENT3 -.- T_SCH
    PDF_GEN -.- T_EXPORT

    %% External API connections
    S3A -.-> GMAPS
    S3B -.-> GMAPS
    S3C -.-> GEMINI
    S5B -.-> GEMINI
    S6A -.-> GEMINI
    S6A -.-> GSEARCH
    AI_REC -.-> GEMINI
    ROI -.-> GEMINI
    PDF_GEN -.-> GEMINI

    %% Data connections
    STEP2 -.- JSON
    STEP4 -.- MONGO
    STEP4 -.- CACHE

    classDef agent fill:#3b82f6,stroke:#1e40af,color:#fff,stroke-width:2px
    classDef tool fill:#10b981,stroke:#059669,color:#fff
    classDef api fill:#f59e0b,stroke:#d97706,color:#000
    classDef data fill:#8b5cf6,stroke:#7c3aed,color:#fff
    classDef external fill:#ef4444,stroke:#dc2626,color:#fff
    classDef post fill:#ec4899,stroke:#db2777,color:#fff

    class AGENT1,AGENT2,AGENT3 agent
    class T_LOC,T_SCH,T_SCORE,T_EXPORT tool
    class API_FIND,API_PIPE,API_REC,API_ROI,API_PDF,API_XLS api
    class JSON,MONGO,CACHE data
    class GMAPS,GEMINI,GSEARCH external
    class AI_REC,ROI,PDF_GEN,XLS_GEN post
```

---

## Agent Responsibilities

### 🤖 Agent 1 — Scraper Agent (`scraper_agent.py`)

Enriches raw park entries with real-world data:

| Step | API Used | Output |
|------|----------|--------|
| Geocoding | Google Find Place + Place Details | Precise lat/lng, place_id, formatted address |
| Logistics | Google Places + Distance Matrix | Distance to highway, railway, airport, port |
| Research | Gemini AI | Water availability, raw materials, incentives, power supply |

### 🤖 Agent 2 — Ranking Agent (`ranking_agent.py`)

Two-phase intelligence:

- **Phase A — Scoring**: 7-category weighted scoring engine producing a score out of 100
- **Phase B — Deep Research**: Gemini generates per-park analysis (why suitable, why attractive, specific benefits, summary paragraph)

### 🤖 Agent 3 — Scheme Agent (`scheme_agent.py`)

Uses Gemini with **Google Search grounding** to find real, currently active government schemes:

- Central government schemes (PLI, CGTMSE, PM Vishwakarma, etc.)
- State-specific industrial policies
- Subsidy stack calculation (total subsidy, net investment, subsidy percentage)

---

## Post-Pipeline Features

| Feature | Trigger | API |
|---------|---------|-----|
| **AI Recommendation** | Auto-loaded per card (async) | `POST /api/ai-recommendation` |
| **ROI Calculator** | On-demand button click | `POST /api/roi-calculator` |
| **PDF Report** | Export button | `POST /api/export/pdf` |
| **Excel Export** | Export button | `POST /api/export/excel` |

---

## Data Flow

```
iilb_parks.json (4,200+ parks)
    ↓ Filter by sector + state + land
Matched Parks (up to 50)
    ↓ Scraper Agent enriches each park
Enriched Parks
    ↓ Store to MongoDB / in-memory cache
    ↓ Ranking Agent scores all parks
Ranked Parks (sorted by score)
    ↓ Top 10 selected
    ↓ Deep Research on each (Gemini)
    ↓ Scheme Agent fetches govt schemes
Final Results (Top 10 with full data)
    ↓ Streamed to frontend via SSE
    ↓ Async AI recommendations loaded
    ↓ ROI + PDF/Excel available on-demand
```

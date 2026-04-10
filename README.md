# 🧠 AI Stock Portfolio Research Agent

An AI-powered full-stack application that analyzes your stock portfolio screenshot and generates a comprehensive research report with per-stock recommendations, technical indicators, news sentiment, macro context, and tomorrow's outlook.

## Architecture

```
Screenshot ──► OCR Agent ──► Data Agent ──► News Agent ──► Technical Agent ──► Macro Agent ──► Report Agent
                 (LLM          (yfinance)    (Tavily +      (RSI, MACD,       (Nifty/Sensex     (Final LLM
                  Vision)                     LLM)           Bollinger)        + LLM outlook)     synthesis)
```

**Backend**: Python / FastAPI with SSE streaming  
**Frontend**: React + TypeScript + Vite + TailwindCSS v4  
**LLM**: Google Gemini Flash 1.5 via OpenRouter (~₹0.15 per analysis)

---

## Prerequisites

| Tool      | Version  | Install                                      |
|-----------|----------|----------------------------------------------|
| Python    | 3.11+    | https://python.org                           |
| Node.js   | 18+      | https://nodejs.org                           |
| Git       | any      | https://git-scm.com                          |

You also need API keys for:
- **OpenRouter** — https://openrouter.ai/keys (for LLM calls)
- **Tavily** — https://tavily.com (for news search)

---

## Setup

### 1. Clone & configure environment variables

```bash
cd stock_research_agent
```

Edit the `.env` file in the project root and add your API keys:

```env
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx
OPENROUTER_MODEL=google/gemini-flash-1.5
TAVILY_API_KEY=tvly-xxxxxxxxxxxxx
```

### 2. Backend setup

```bash
# Create a virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 3. Frontend setup

```bash
cd frontend
npm install
cd ..
```

---

## Running the Application

You need **two terminals** — one for the backend, one for the frontend.

### Terminal 1 — Backend (FastAPI)

```bash
# From the project root, with venv activated
uvicorn backend.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.

### Terminal 2 — Frontend (Vite dev server)

```bash
cd frontend
npm run dev
```

The UI will be available at `http://localhost:5173`.  
API calls from the frontend are proxied to `localhost:8000` automatically.

---

## Usage

1. Open `http://localhost:5173` in your browser.
2. Upload a screenshot of your stock portfolio (PNG/JPG) — for example, a Zerodha/Groww holdings page.
3. Watch the 6-step agent pipeline execute in real time with SSE streaming.
4. View the final research report with:
   - Portfolio health score & overall recommendation
   - Per-stock analysis (rating, tomorrow's outlook, catalysts, risks, action)
   - Technical indicators (RSI, MACD, Bollinger Bands)
   - News sentiment analysis
   - Macro context (Nifty, Sensex, global cues)
   - Rebalancing suggestions
5. Download the report as a PDF.

---

## Project Structure

```
stock_research_agent/
├── .env                          # API keys (not committed)
├── .gitignore
├── README.md
├── backend/
│   ├── requirements.txt
│   ├── __init__.py
│   ├── main.py                   # FastAPI app & endpoints
│   ├── llm_client.py            # OpenRouter LLM wrapper
│   ├── models/
│   │   ├── portfolio.py         # Holding, Portfolio models
│   │   └── report.py            # Report Pydantic models
│   ├── tools/
│   │   ├── stock_data.py        # yfinance helpers
│   │   ├── news_fetcher.py      # Tavily news search
│   │   └── calculations.py      # RSI, MACD, SMA, Bollinger
│   ├── agents/
│   │   ├── ocr_agent.py         # Vision-based OCR
│   │   ├── data_agent.py        # Market data enrichment
│   │   ├── news_agent.py        # News + sentiment
│   │   ├── technical_agent.py   # Technical indicators
│   │   ├── macro_agent.py       # Macro context
│   │   ├── report_agent.py      # Final report synthesis
│   │   └── pipeline.py          # Agent orchestrator
│   └── utils/
│       └── pdf_export.py        # PDF report generation
└── frontend/
    ├── package.json
    ├── vite.config.ts
    ├── index.html
    └── src/
        ├── main.tsx
        ├── App.tsx               # Main app with phase routing
        ├── index.css             # TailwindCSS v4 theme
        ├── types.ts              # TypeScript interfaces
        ├── hooks/
        │   └── useAgentStream.ts # SSE streaming hook
        └── components/
            ├── UploadScreen.tsx
            ├── AgentStepCard.tsx
            ├── AgentTracePanel.tsx
            ├── StockCard.tsx
            ├── TrendChart.tsx
            ├── NewsPanel.tsx
            └── ReportDashboard.tsx
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `OPENROUTER_API_KEY not set` | Make sure `.env` is in the project root with valid keys |
| `ModuleNotFoundError` | Activate your venv: `venv\Scripts\activate` |
| Frontend can't reach API | Ensure backend is running on port 8000 |
| OCR returns empty portfolio | Use a clear, high-resolution screenshot with visible ticker names and quantities |
| yfinance errors for Indian stocks | The app auto-appends `.NS` (NSE) suffix; if your stocks are on BSE, the OCR agent handles `.BO` too |

---

## Tech Stack

- **LLM**: Google Gemini Flash 1.5 via OpenRouter (multimodal — text + vision)
- **Backend**: FastAPI, yfinance, Tavily, fpdf2, SSE-Starlette
- **Frontend**: React 19, TypeScript, Vite, TailwindCSS v4, Recharts, Framer Motion
- **Streaming**: Server-Sent Events (SSE) for real-time agent progress

---

## Deployment (Render + Vercel)

Deploy the backend on **Render** (free) and the frontend on **Vercel** (free) to access the app from any device.

**GitHub repo**: https://github.com/charizard00001/stock_research_agent  
**Frontend (Vercel)**: https://frontend-eight-zeta-11.vercel.app *(already deployed & connected to GitHub — auto-deploys on push)*

### 1. Deploy Backend on Render

1. Go to [render.com](https://render.com) and sign up / log in with your **GitHub account**.
2. Click **New → Web Service**.
3. Click **Connect a repository** and select `charizard00001/stock_research_agent`.
4. Configure the service:

| Setting | Value |
|---------|-------|
| **Name** | `equilyze-api` |
| **Region** | Singapore (or closest to you) |
| **Runtime** | Docker |
| **Dockerfile Path** | `./Dockerfile` |
| **Instance Type** | Free |

5. Scroll down to **Environment Variables** and add:

| Key | Value |
|-----|-------|
| `OPENROUTER_API_KEY` | Your OpenRouter API key |
| `TAVILY_API_KEY` | Your Tavily API key |
| `FRONTEND_URL` | `https://frontend-eight-zeta-11.vercel.app` |

6. Click **Create Web Service**. Render will build from the `Dockerfile` and deploy.
7. Wait for the build to finish (first build takes 3-5 min).
8. Once live, your backend URL will be: `https://equilyze-api.onrender.com`
9. Verify: open `https://equilyze-api.onrender.com/api/health` — should return `{"status": "ok"}`.

> **Note**: Free tier spins down after 15 min of inactivity. First request after idle takes ~30-50s to cold start.

### 2. Update Backend URL in vercel.json (if needed)

The `frontend/vercel.json` is already configured to proxy `/api/*` to `https://equilyze-api.onrender.com`. If you chose a different service name on Render, update it:

```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://<your-actual-render-name>.onrender.com/api/:path*"
    }
  ]
}
```

Then push the change:
```bash
git add frontend/vercel.json
git commit -m "fix: update backend URL"
git push
```
Vercel will auto-redeploy.

### 3. Verify End-to-End

1. Open your Vercel URL: https://frontend-eight-zeta-11.vercel.app
2. You should see the upload screen with a model selection dropdown.
3. Upload a portfolio screenshot and select a model.
4. The analysis should run through all 6 agents and display the report.
5. Chat should work using the same selected model.

### Troubleshooting Deployment

| Issue | Fix |
|-------|-----|
| Render build fails | Check the build logs — usually a missing dependency or Dockerfile issue |
| Frontend loads but API calls fail | Check that `vercel.json` has the correct Render URL |
| CORS errors in browser console | Verify `FRONTEND_URL` env var on Render matches your Vercel URL exactly (including `https://`) |
| Render returns 502/503 | The free instance is cold-starting — wait 30-50s and retry |
| Changes not reflecting | Push to GitHub — both Render and Vercel auto-deploy on push |

### Deployment Files Reference

| File | Purpose |
|------|---------|
| `Dockerfile` | Backend container image for Render |
| `.dockerignore` | Excludes frontend, venv, .env from Docker build |
| `render.yaml` | Render Blueprint (optional — used if you click "New from Blueprint") |
| `frontend/vercel.json` | Rewrites `/api/*` requests to the Render backend |

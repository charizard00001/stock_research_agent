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

### 1. Push to GitHub

Your repo must be on GitHub for both services to connect.

```bash
git init
git add .
git commit -m "initial commit"
git remote add origin https://github.com/<your-username>/stock_research_agent.git
git push -u origin main
```

### 2. Deploy Backend on Render

1. Go to [render.com](https://render.com) and sign up / log in (GitHub login recommended).
2. Click **New → Web Service**.
3. Connect your GitHub repo (`stock_research_agent`).
4. Configure the service:

| Setting | Value |
|---------|-------|
| **Name** | `equilyze-api` |
| **Region** | Singapore (or closest to you) |
| **Runtime** | Docker |
| **Instance Type** | Free |

5. Add **Environment Variables** (under the "Environment" section):

| Key | Value |
|-----|-------|
| `OPENROUTER_API_KEY` | Your OpenRouter API key |
| `TAVILY_API_KEY` | Your Tavily API key |
| `FRONTEND_URL` | *(leave blank for now, set after Vercel deploy)* |

6. Click **Create Web Service**. Render will build from the `Dockerfile` and deploy.
7. Once live, your backend URL will be: `https://equilyze-api.onrender.com`

> **Note**: Free tier spins down after 15 min of inactivity. First request after idle takes ~30-50s.

### 3. Deploy Frontend on Vercel

1. Go to [vercel.com](https://vercel.com) and sign up / log in.
2. Click **Add New → Project** and import your GitHub repo.
3. Configure the project:

| Setting | Value |
|---------|-------|
| **Framework Preset** | Vite |
| **Root Directory** | `frontend` |

4. Click **Deploy**. Vercel will build and deploy automatically.
5. Your frontend URL will be something like: `https://your-project.vercel.app`

**Or use the Vercel CLI:**

```bash
cd frontend
npm i -g vercel
vercel login
vercel --prod
```

### 4. Wire Everything Together

After both are deployed:

1. **Update `vercel.json`** — Replace the backend URL if your Render service name differs from `equilyze-api`:

```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://<your-render-service>.onrender.com/api/:path*"
    }
  ]
}
```

2. **Set `FRONTEND_URL` on Render** — Go to your Render service → Environment → add:

| Key | Value |
|-----|-------|
| `FRONTEND_URL` | `https://your-project.vercel.app` |

3. **Redeploy both** — Push a commit or trigger manual deploys on both services.

### 5. Verify

- Visit your Vercel URL — the upload screen should load.
- Check backend health: `https://equilyze-api.onrender.com/api/health` should return `{"status": "ok"}`.
- Upload a portfolio screenshot and run a full analysis.

### Deployment Files Reference

| File | Purpose |
|------|---------|
| `Dockerfile` | Backend container image for Render |
| `.dockerignore` | Excludes frontend, venv, .env from Docker build |
| `render.yaml` | Render Blueprint (optional one-click deploy) |
| `frontend/vercel.json` | Rewrites `/api/*` requests to the Render backend |

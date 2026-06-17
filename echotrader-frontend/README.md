# EchoTrader Dashboard

Production frontend for the EchoTrader reflexive market mirror agent. Institutional dark/light themes, live perception history, and execution transparency.

**Live:** https://echotrader.vercel.app

## Architecture

```mermaid
flowchart TB
    subgraph Client["Next.js Dashboard"]
        UI[Market Mirror UI]
        Theme[Theme Toggle + Persistence]
        Chart[Fear and Greed History]
    end

    subgraph API["FastAPI — api/server.py"]
        Status["/api/status"]
        Refresh["/api/status?refresh=true"]
    end

    subgraph Agent["Python Agent Core"]
        P[Perception Layer]
        R[Reasoner]
        G[Risk Guard]
        E[TWAK Executor]
    end

    subgraph Memory["Local State"]
        EchoLog[echo_log.jsonl]
        Trades[trades.log]
        Lessons[lessons.md]
    end

    UI --> Status
    Theme --> UI
    Chart --> Status
    Refresh --> P
    Status --> EchoLog
    Status --> Trades
    P --> R --> G --> E
    R --> Lessons
    P --> EchoLog
    E --> Trades
```

## Data Flow

```mermaid
sequenceDiagram
    participant User
    participant Dashboard
    participant API
    participant Perception
    participant Reasoner

    User->>Dashboard: Open /
    Dashboard->>API: GET /api/status
    API-->>Dashboard: perception, reasoner, history, trades

    User->>Dashboard: Refresh Agent
    Dashboard->>API: GET /api/status?refresh=true
    API->>Perception: perceive()
    Perception->>Reasoner: think()
    API-->>Dashboard: updated snapshot

    User->>Dashboard: Toggle theme
    Dashboard->>Dashboard: localStorage echotrader-theme
```

## Local Development

```bash
# Terminal 1 — Python API (repo root)
python -m api.server

# Terminal 2 — Dashboard
npm install
cp .env.example .env.local
npm run dev
```

Open http://localhost:3000

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | FastAPI backend URL (e.g. `http://localhost:8000`) |

No API keys belong in the frontend. All secrets stay in the Python backend `.env`.

## Brand Assets

| Asset | Path | Purpose |
|-------|------|---------|
| Favicon | `public/icon.svg` | Browser tab — echo mirror mark |
| Apple icon | `public/apple-icon.svg` | iOS home screen |
| Open Graph | `public/og.svg` | Social / link previews |

## Deploy to Vercel

1. Import with root directory `echotrader-frontend`
2. Set in Vercel dashboard:
   - `NEXT_PUBLIC_SITE_URL` = `https://echotrader.vercel.app`
   - `NEXT_PUBLIC_API_URL` = your deployed FastAPI host
3. Add to backend `.env`: `CORS_ORIGINS=https://echotrader.vercel.app`
4. Deploy — `npm run build` verified locally

`vercel.json` included. Theme preference persists client-side via `localStorage`.
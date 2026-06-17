# EchoTrader Dashboard

Production frontend for the EchoTrader reflexive market mirror agent.

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

## Deploy to Vercel

1. Import this folder (or monorepo with root directory `echotrader-frontend`)
2. Set `NEXT_PUBLIC_API_URL` to your deployed FastAPI host
3. Deploy — `npm run build` must pass (verified locally)

`vercel.json` is included. Add backend CORS for your Vercel domain before going live.
# Devenira - Health & Wellness App

AI-powered health and wellness application with calorie tracking, body analysis, workout logging, and transformation previews.

## Features

### Free Tier
- Calorie counter & food logging with trend graphs
- AI food photo analysis (5 free scans)
- Workout tracker with exercise library
- Body fat estimation (1 free scan)
- Percentile ranking (1 free comparison)

### Premium
- Unlimited AI food photo analysis
- Unlimited body scans & transformation previews
- Photo enhancement (professional retouching)
- Advanced analytics & projections
- Weight goal tracking with TDEE calculations

## Architecture

```
fromFatToFit_v2/
├── backend/             # FastAPI (Python)
│   ├── app/
│   │   ├── core/        # Config, Supabase clients, auth dependency
│   │   ├── domains/     # One package per feature (router, schemas, services)
│   │   ├── integrations/ # OpenAI, Anthropic, Gemini, Grok, Replicate
│   │   └── vision/      # Local CPU vision models
│   ├── db/              # schema.sql + numbered migrations
│   ├── scripts/         # One-off maintenance scripts (transcript ingest, QA user)
│   └── requirements.txt
│
├── frontend/            # Next.js (React/TypeScript)
│   └── src/
│       ├── app/         # Pages & layouts
│       ├── components/  # UI components
│       ├── lib/         # API client & utilities
│       ├── contexts/    # React contexts
│       └── types/       # TypeScript definitions
│
├── mobile/              # React Native (Expo)
│   └── src/
│       ├── screens/     # App screens
│       ├── services/    # API clients
│       └── theme/       # Design system
│
├── tests/               # Playwright API/E2E tests, HTTP sweep, fixtures
├── scripts/             # Dev tooling (Bitwarden .env pull/check)
├── docs/                # Setup, deploy, design and QA docs (old reports in docs/archive/)
├── marketing/           # Blog strategy, drafts, Medium/SEO tools
└── content/transcripts/ # YouTube transcripts for the coach RAG ingest
```

## Tech Stack

- **Backend**: FastAPI, Supabase (PostgreSQL + Auth), Python 3.11+
- **Frontend**: Next.js 14, React, TypeScript, Tailwind CSS, shadcn/ui
- **Mobile**: React Native, Expo
- **AI**: OpenAI (GPT-4o, GPT-Image-1), Gemini, Claude, Grok
- **Payments**: Stripe (web), RevenueCat (mobile)

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- [Supabase](https://supabase.com) account
- OpenAI API key

### Local env files

Secrets live in Bitwarden (`Devenira backend .env`, `Devenira frontend .env.local`).
With the Bitwarden CLI installed (`winget install Bitwarden.CLI`):

```powershell
powershell -ExecutionPolicy Bypass -File scripts\pull-secrets.ps1   # writes backend/.env, frontend/.env.local
powershell -ExecutionPolicy Bypass -File scripts\check-secrets.ps1  # compares Bitwarden notes with .env.example
```

Without Bitwarden, copy `backend/.env.example` and `frontend/.env.local.example` and fill them in.

#### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

#### Mobile

```bash
cd mobile
npm install
cp .env.example .env
npm start
```

## Environment Variables

See `backend/.env.example` and `frontend/.env.local.example` for all required configuration.

Key variables:
- `SUPABASE_URL` / `SUPABASE_ANON_KEY` / `SUPABASE_SERVICE_KEY`
- `OPENAI_API_KEY` (required)
- `GEMINI_API_KEY`, `GROK_API_KEY`, `ANTHROPIC_API_KEY` (optional)
- `AI_PROVIDER` - Select primary AI: `openai`, `gemini`, `claude`, `grok`, `hybrid`
- `STRIPE_SECRET_KEY` / `STRIPE_WEBHOOK_SECRET`

## API Documentation

Backend API docs available at `http://localhost:8000/docs` when running locally.

### Key Endpoints

| Category | Endpoint | Description |
|----------|----------|-------------|
| Auth | `POST /api/auth/register` | Create account |
| Auth | `POST /api/auth/login` | Sign in |
| Food | `POST /api/food/analyze-photo` | AI food analysis |
| Food | `GET /api/food/trends` | Calorie trends |
| Body | `POST /api/body/estimate-bodyfat` | Body fat estimation |
| Body | `POST /api/body/transformation` | Transformation preview |
| Body | `POST /api/body/enhancement` | Photo enhancement |
| Workout | `POST /api/workout/log` | Log workout |
| Weight | `POST /api/weight/log` | Log weight |
| Payments | `POST /api/payments/create-checkout-session` | Stripe checkout |

## License

Proprietary - All rights reserved

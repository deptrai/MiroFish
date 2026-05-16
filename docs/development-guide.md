# MiroFish - Development Guide

**Date:** 2026-05-17

## Prerequisites

- Node.js `>=18`
- Python `>=3.11` and typically `<=3.12` for dependency compatibility
- `uv` (Python package manager)

## Environment Setup

1. Copy env file:

```bash
cp .env.example .env
```

2. Set required keys:
- `LLM_API_KEY`
- `ZEP_API_KEY`

Optional:
- `LLM_BASE_URL`
- `LLM_MODEL_NAME`

## Install Dependencies

Recommended:

```bash
npm run setup:all
```

Or split:

```bash
npm run setup
npm run setup:backend
```

## Run Locally

Start both frontend and backend:

```bash
npm run dev
```

Services:
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:5001`

Run separately:

```bash
npm run backend
npm run frontend
```

## Build

```bash
npm run build
```

## Testing and Validation

- Backend script smoke:
```bash
cd backend
uv run python run.py
```
- API smoke:
```bash
curl http://localhost:5001/health
```
- Frontend smoke: open `http://localhost:3000` and validate step flow rendering.

## Docker

```bash
docker compose up -d
```

Maps:
- `3000:3000`
- `5001:5001`

## Common Troubleshooting

- Missing backend startup keys:
  - Ensure `.env` has `LLM_API_KEY` and `ZEP_API_KEY`.
- Python dependency failures on 3.13:
  - Use Python 3.12 for better wheel compatibility.

---

_Generated using BMAD Method `document-project` workflow_

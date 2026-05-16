# MiroFish - Source Tree Analysis

**Date:** 2026-05-17

## Overview

MiroFish is organized as a two-part repository: `frontend/` for the web application and `backend/` for API + simulation orchestration.

## Complete Directory Structure

```text
MiroFish/
├── frontend/
│   ├── src/
│   │   ├── api/            # Axios API clients for graph/simulation/report
│   │   ├── components/     # Step-based workflow UI components
│   │   ├── views/          # Route-level pages
│   │   ├── router/         # Vue Router definitions
│   │   ├── i18n/           # Locale bootstrapping
│   │   └── store/          # Lightweight shared client state
│   ├── public/
│   └── vite.config.js
├── backend/
│   ├── app/
│   │   ├── api/            # Flask Blueprint routes
│   │   ├── services/       # Graph, profile, simulation, report logic
│   │   ├── models/         # Domain/state models
│   │   ├── utils/          # Parsing, logging, retry, helpers
│   │   ├── config.py       # Environment-driven runtime config
│   │   └── __init__.py     # App factory and middleware wiring
│   ├── scripts/            # Twitter/Reddit simulation runner scripts
│   └── run.py              # Backend entry point
├── locales/                # en/zh language packs
├── static/                 # images/screenshots
├── docker-compose.yml
├── Dockerfile
└── README.md
```

## Critical Directories

### `frontend/src/views`

Route-level screens implementing the end-user workflow from upload to report/interaction.

### `frontend/src/components`

Reusable workflow blocks (`Step1GraphBuild` ... `Step5Interaction`) plus graph/report panels.

### `backend/app/api`

HTTP interface layer with three namespaces:
- `/api/graph`
- `/api/simulation`
- `/api/report`

### `backend/app/services`

Core orchestration and domain behavior:
- graph build on Zep
- entity/profile generation
- simulation lifecycle
- report generation and tool-backed querying

### `backend/scripts`

Long-running OASIS simulation processes and IPC-compatible execution scripts.

## Entry Points

- Frontend app: `frontend/src/main.js`
- Frontend router: `frontend/src/router/index.js`
- Backend app boot: `backend/run.py`
- Backend Flask factory: `backend/app/__init__.py`

## Configuration Files

- `package.json` (root script orchestrator)
- `frontend/package.json`
- `backend/pyproject.toml`
- `.env` / `.env.example`
- `docker-compose.yml`
- `Dockerfile`

---

_Generated using BMAD Method `document-project` workflow_

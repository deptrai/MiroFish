# MiroFish - Project Overview

**Date:** 2026-05-17
**Type:** Multi-part web + backend project
**Architecture:** Vue SPA + Flask API + OASIS simulation workers

## Executive Summary

MiroFish is an AI prediction engine that transforms uploaded seed documents into a knowledge graph, generates simulation agents, runs dual-platform social simulations (Twitter-like and Reddit-like), and produces interactive reports.

## Project Classification

- **Repository Type:** Multi-part monorepo (frontend + backend)
- **Project Type(s):** `web` (frontend) + `backend` (backend service)
- **Primary Language(s):** JavaScript (Vue), Python (Flask)
- **Architecture Pattern:** Service-oriented backend with step-based UI workflow

## Multi-Part Structure

### Frontend

- **Type:** Web SPA
- **Location:** `frontend/`
- **Purpose:** User workflow for graph build, env setup, simulation run, report, and interaction
- **Tech Stack:** Vue 3, Vue Router, Vue I18n, Axios, D3, Vite

### Backend

- **Type:** API + orchestration service
- **Location:** `backend/`
- **Purpose:** Graph generation, simulation orchestration, report generation, IPC with simulation scripts
- **Tech Stack:** Flask, Pydantic, OpenAI SDK-compatible client, Zep Cloud, camel-oasis

### How Parts Integrate

Frontend calls backend REST APIs under `/api/graph`, `/api/simulation`, and `/api/report` via Axios. Backend stores runtime artifacts under `backend/uploads/` and coordinates long-running simulations with script-based workers.

## Technology Stack Summary

| Category | Technology | Version |
|---|---|---|
| Frontend Framework | Vue | ^3.5.24 |
| Frontend Router | vue-router | ^4.6.3 |
| Frontend Build | Vite | ^7.2.4 |
| Frontend HTTP | Axios | ^1.14.0 |
| Backend Framework | Flask | >=3.0.0 |
| Backend Config | python-dotenv | >=1.0.0 |
| AI/LLM SDK | openai | >=1.0.0 |
| Graph Memory | zep-cloud | 3.13.0 |
| Simulation | camel-oasis / camel-ai | 0.2.5 / 0.2.78 |
| Python Runtime | CPython | 3.11-3.12 recommended |

## Key Features

- Upload PDF/MD/TXT seed files
- Auto-generate ontology and build graph on Zep
- Generate OASIS agent profiles and simulation config
- Run Twitter-like and Reddit-like parallel simulations
- Generate report and interactive Q&A with report/simulated agents

## Repository Structure

- `frontend/`: Vue SPA
- `backend/app/api`: REST endpoints
- `backend/app/services`: core business and orchestration logic
- `backend/scripts`: simulation worker scripts
- `locales/`: i18n translation files
- `static/`: marketing/demo images

---

_Generated using BMAD Method `document-project` workflow_

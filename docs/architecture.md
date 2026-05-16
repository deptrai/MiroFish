# MiroFish - Architecture

**Date:** 2026-05-17
**Style:** Layered multi-service application (UI + API + simulation worker scripts)

## Executive Summary

The architecture uses a Vue SPA as orchestration UI and a Flask backend as stateful pipeline coordinator. The backend integrates with Zep Cloud for graph memory and OASIS/CAMEL components for simulation execution.

## Topology

1. User uploads source documents (PDF/MD/TXT) from frontend.
2. Backend parses documents, generates ontology, and builds graph in Zep.
3. Backend filters entities and generates simulation profiles/config.
4. Backend starts simulation scripts (Twitter-like and Reddit-like).
5. Simulation artifacts are persisted under `backend/uploads/simulations`.
6. Report APIs consume graph + simulation outputs for report generation and interaction.

## Backend Architecture

### API Layer

- `backend/app/api/graph.py`
- `backend/app/api/simulation.py`
- `backend/app/api/report.py`

All routes are registered via Flask Blueprints in `backend/app/api/__init__.py`.

### Service Layer

- `graph_builder.py`: graph and ontology integration with Zep
- `simulation_manager.py` / `simulation_runner.py`: lifecycle orchestration
- `oasis_profile_generator.py`: entity-to-agent conversion
- `report_agent.py`: post-simulation report generation and Q&A support
- `zep_*` services: graph entity read/search/update utilities

### Utility Layer

- `file_parser.py`: PDF/MD/TXT extraction
- retry/logging/paging utilities for robust integration behavior

## Frontend Architecture

### Routing

Primary routes:
- `/` home/upload
- `/process/:projectId`
- `/simulation/:simulationId`
- `/simulation/:simulationId/start`
- `/report/:reportId`
- `/interaction/:reportId`

### UI Composition

The app centers around step components and workflow views:
- `Step1GraphBuild` → graph generation
- `Step2EnvSetup` → profile/config preparation
- `Step3Simulation` → runtime status and controls
- `Step4Report` → report generation/inspection
- `Step5Interaction` → conversational interaction

## Data and Runtime Artifacts

- Upload and simulation data live under `backend/uploads/`
- Reports and generated files are persisted by backend managers
- IPC between Flask and worker scripts is file-based for command/response handoff

## Configuration and Environments

- Required env keys: `LLM_API_KEY`, `ZEP_API_KEY`
- Optional model settings via `LLM_BASE_URL`, `LLM_MODEL_NAME`
- Root-level `npm run dev` starts frontend + backend concurrently

## Constraints and Non-Goals

- This project does not include built-in internet crawler ingestion by default.
- Production hardening (observability, queueing, distributed workers) is limited in this open-source baseline.

---

_Generated using BMAD Method `document-project` workflow_

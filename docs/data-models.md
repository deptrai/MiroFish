# MiroFish - Data Models

**Date:** 2026-05-17

## Model Locations

- `backend/app/models/project.py`
- `backend/app/models/task.py`
- API/domain payloads are heavily represented through dictionaries and Pydantic-like structures in service/API layers.

## Persistent Runtime Data

The system stores operational artifacts on filesystem rather than a conventional SQL schema:

- `backend/uploads/` - uploaded source files
- `backend/uploads/simulations/{simulation_id}/` - simulation artifacts, configs, logs, IPC files
- `backend/uploads/reports/` - generated report artifacts

## Key Conceptual Entities

- **Project**: graph-build lifecycle context, ontology, source files, graph id
- **Task**: async progress tracking for graph/simulation/report operations
- **Simulation**: run metadata, config, state, status, timeline, posts/comments
- **Report**: generated narrative output + agent logs + interaction context
- **Graph Entity**: Zep node abstraction used for profile generation and retrieval
- **Agent Profile**: OASIS-compatible profile derived from graph entities

## External Data Dependencies

- Zep Cloud graph storage (`zep-cloud`)
- OASIS simulation formats:
  - Twitter profiles (CSV)
  - Reddit profiles (JSON)

## Validation and Constraints

- Upload formats: `.pdf`, `.md`, `.txt`, `.markdown`
- Max upload size: 50 MB
- Required env-backed integration keys: `LLM_API_KEY`, `ZEP_API_KEY`

## Schema Evolution

No first-class migration tool (Alembic/Flyway/Prisma) is present in this repository. Evolution is primarily code-and-file-format driven.

---

_Generated using BMAD Method `document-project` workflow_

# MiroFish - API Contracts

**Date:** 2026-05-17
**Base URL:** `http://localhost:5001`

## Namespaces

- `/api/graph`
- `/api/simulation`
- `/api/report`

## Graph APIs (selected)

- `POST /api/graph/ontology/generate` - generate ontology from uploaded content + requirement text
- `POST /api/graph/build` - build graph in Zep
- `GET /api/graph/project/{project_id}` - read project details
- `GET /api/graph/project/list` - list projects
- `GET /api/graph/data/{graph_id}` - fetch graph data for visualization
- `DELETE /api/graph/delete/{graph_id}` - remove graph

## Simulation APIs (selected)

- `POST /api/simulation/create` - create simulation record
- `POST /api/simulation/prepare` - generate profiles/config and prepare run
- `POST /api/simulation/start` - start simulation
- `POST /api/simulation/stop` - stop simulation
- `GET /api/simulation/{simulation_id}/run-status` - fetch run status
- `GET /api/simulation/{simulation_id}/timeline` - simulation timeline data
- `GET /api/simulation/{simulation_id}/posts` - generated posts
- `GET /api/simulation/{simulation_id}/comments` - generated comments
- `POST /api/simulation/interview` - interview single agent
- `POST /api/simulation/interview/batch` - batch interview

## Report APIs (selected)

- `POST /api/report/generate` - generate report
- `POST /api/report/generate/status` - report generation status
- `GET /api/report/{report_id}` - fetch report details/content
- `POST /api/report/chat` - conversational query over report/simulation context
- `GET /api/report/{report_id}/agent-log` - report generation agent logs
- `GET /api/report/{report_id}/console-log` - report generation console logs

## Health

- `GET /health` - backend health check endpoint

## Notes

- CORS is enabled for `/api/*`.
- Long-running operations expose polling/status endpoints.
- Exact request/response schemas should be derived from endpoint handlers in:
  - `backend/app/api/graph.py`
  - `backend/app/api/simulation.py`
  - `backend/app/api/report.py`

---

_Generated using BMAD Method `document-project` workflow_

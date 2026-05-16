---
project_name: "MiroFish"
user_name: "Luisphan"
date: "2026-05-17"
sections_completed:
  - technology_stack
  - language_rules
  - framework_rules
  - testing_rules
  - quality_rules
  - workflow_rules
  - anti_patterns
status: "complete"
rule_count: 24
optimized_for_llm: true
---

# Project Context for AI Agents

_This file contains critical rules and patterns that AI agents must follow when implementing code in this project. Focus on unobvious details that agents might otherwise miss._

---

## Technology Stack & Versions

- **Frontend:** Vue `^3.5.24`, Vue Router `^4.6.3`, Vue I18n `^11.3.0`, Vite `^7.2.4`, Axios `^1.14.0`, D3 `^7.9.0`
- **Backend:** Python `>=3.11` (project runtime is more stable on 3.12 for dependency wheels), Flask `>=3.0.0`, Flask-CORS `>=6.0.0`, Pydantic `>=2.0.0`
- **AI/Simulation:** OpenAI SDK `>=1.0.0`, Zep Cloud `3.13.0`, camel-oasis `0.2.5`, camel-ai `0.2.78`
- **File Parsing:** PyMuPDF `>=1.24.0`, charset-normalizer `>=3.0.0`, chardet `>=5.0.0`
- **Tooling:** `uv` for Python env/deps, npm for Node deps, concurrently for dual service dev startup

## Critical Implementation Rules

### Language-Specific Rules

- Keep backend API responses and logs UTF-8 friendly; the app intentionally disables ASCII escaping for JSON output.
- Do not remove config validation gates for `LLM_API_KEY` and `ZEP_API_KEY`; backend startup depends on them.
- Keep Python import paths relative to current backend package structure (`backend/app/...`) and avoid ad hoc path hacks except in scripts that already do bootstrap path insertion.
- Preserve existing bilingual code-comment style where present; do not mass-convert comments/literals unless requested.

### Framework-Specific Rules

- Frontend routing is history-mode Vue Router with parameterized paths (`/process/:projectId`, `/simulation/:simulationId`, `/report/:reportId`, `/interaction/:reportId`); new pages should follow this pattern.
- Frontend API calls are structured under `frontend/src/api/*` and target Flask namespaces (`/api/graph`, `/api/simulation`, `/api/report`); keep this separation.
- Backend endpoints are organized with Flask Blueprints and explicit URL prefixes; add routes to existing blueprints instead of creating parallel ad hoc apps.
- CORS is enabled specifically for `/api/*`; keep new API paths under `/api/` unless there is a strong reason not to.

### Testing Rules

- Prefer script-level or endpoint-level verification when changing simulation/report pipelines; these flows are heavily async and integration-oriented.
- For UI changes, verify primary route rendering and core actions on local dev server (`http://localhost:3000`) before claiming completion.
- For backend changes touching file parsing or config validation, include at least one direct run path (`uv run python run.py` or API call smoke test).

### Code Quality & Style Rules

- Keep modifications scoped: this repo has large feature modules, so avoid cross-module refactors unless required by the task.
- Respect current folder boundaries:
  - `frontend/src/views` for page-level views
  - `frontend/src/components` for step/tool components
  - `backend/app/services` for business logic
  - `backend/app/api` for HTTP wiring
- Reuse existing service abstractions (`simulation_manager`, `report_agent`, `zep_*`) rather than duplicating orchestration logic.
- Preserve existing script entrypoints and CLI behavior in root `package.json`.

### Development Workflow Rules

- Standard local startup path is:
  - `npm run setup:all`
  - `npm run dev`
- Backend dependency management is `uv`-first; do not switch to unrelated environment managers inside repo docs/scripts without explicit request.
- Environment variables are expected in project root `.env`; keep `.env.example` synchronized with any new required vars.
- Do not commit generated upload data under `backend/uploads/` or local runtime logs.

### Critical Don't-Miss Rules

- Do not assume the project auto-crawls websites; core flow is user-uploaded files (`pdf`, `md`, `txt`) -> ontology/graph -> simulation.
- Do not break Zep graph flow assumptions: graph IDs and entity extraction are shared across simulation and reporting features.
- Do not change OASIS output format contracts casually (Twitter CSV vs Reddit JSON handling is intentional).
- Avoid introducing blocking synchronous behavior into long simulation/report flows; existing design uses async/polling/progress state.
- Keep security-sensitive values out of repo (`.env` is gitignored).

---

## Usage Guidelines

**For AI Agents:**

- Read this file before implementing any code.
- Follow all rules unless the user explicitly requests an exception.
- Prefer existing architecture patterns over new abstractions.
- Update this context when foundational stack/workflow rules change.

**For Humans:**

- Keep this file concise and practical.
- Update after major dependency or architecture changes.
- Remove rules that become obsolete or too obvious.

Last Updated: 2026-05-17

# MiroFish - Component Inventory

**Date:** 2026-05-17

## Frontend View Components

- `Home.vue` - upload-first landing and workflow entry
- `MainView.vue` / `Process.vue` - process orchestration and graph analysis views
- `SimulationView.vue` - simulation detail viewer
- `SimulationRunView.vue` - simulation runtime view
- `ReportView.vue` - report presentation container
- `InteractionView.vue` - interactive chat and investigation flow

## Workflow Step Components

- `Step1GraphBuild.vue` - ontology + graph construction phase
- `Step2EnvSetup.vue` - entity selection, profile generation, config prep
- `Step3Simulation.vue` - start/stop/status runtime control
- `Step4Report.vue` - report generation and report-level analytics
- `Step5Interaction.vue` - post-report interactions

## Shared/Utility UI Components

- `GraphPanel.vue` - graph visualization and node details
- `HistoryDatabase.vue` - historical records and artifact browsing
- `LanguageSwitcher.vue` - locale switching control

## Client API Modules

- `frontend/src/api/graph.js`
- `frontend/src/api/simulation.js`
- `frontend/src/api/report.js`
- `frontend/src/api/index.js` (HTTP client setup + retry integration)

## Notes

- UI follows step-driven workflow rather than isolated feature pages.
- i18n resources are maintained under `locales/` and `frontend/src/i18n/`.

---

_Generated using BMAD Method `document-project` workflow_

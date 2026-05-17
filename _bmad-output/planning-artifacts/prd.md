---
stepsCompleted: ["step-01-init", "step-02-discovery", "step-02b-vision", "step-02c-executive-summary", "step-03-success"]
inputDocuments:
  - "/Users/luisphan/Documents/GitHub/MiroFish/_bmad-output/project-context.md"
  - "/Users/luisphan/Documents/GitHub/MiroFish/docs/index.md"
  - "/Users/luisphan/Documents/GitHub/MiroFish/docs/project-overview.md"
  - "/Users/luisphan/Documents/GitHub/MiroFish/docs/architecture.md"
  - "/Users/luisphan/Documents/GitHub/MiroFish/docs/source-tree-analysis.md"
  - "/Users/luisphan/Documents/GitHub/MiroFish/docs/component-inventory.md"
  - "/Users/luisphan/Documents/GitHub/MiroFish/docs/api-contracts.md"
  - "/Users/luisphan/Documents/GitHub/MiroFish/docs/data-models.md"
  - "/Users/luisphan/Documents/GitHub/MiroFish/docs/development-guide.md"
documentCounts:
  briefCount: 0
  researchCount: 0
  brainstormingCount: 0
  projectDocsCount: 9
workflowType: "prd"
classification:
  projectType: "web_app"
  domain: "scientific"
  complexity: "medium"
  projectContext: "brownfield"
---

# Product Requirements Document - MiroFish

**Author:** Luisphan
**Date:** 2026-05-17

## Executive Summary

MiroFish is a brownfield AI prediction platform that turns unstructured seed materials into an executable simulation pipeline for decision rehearsal. Instead of stopping at document summarization, it builds a graph-backed world model, instantiates social agents, and runs dual-platform simulations to surface trajectory signals before real-world outcomes unfold.

The product is designed for teams that need to evaluate policy, narrative, or market scenarios under uncertainty. The core value is practical foresight: users can inject assumptions, observe emergent behavior over time, and iterate on decisions with evidence generated from simulation dynamics rather than static analysis alone.

### What Makes This Special

MiroFish differentiates through an end-to-end operational chain: `document ingestion -> ontology and graph construction -> multi-agent simulation -> report and interactive interrogation`. This integration creates a feedback loop where knowledge representation and behavior generation reinforce each other.

The core insight is that prediction quality improves when structured context (graph memory) is coupled with time-evolving agent interaction. Static analysis can identify facts and relationships; simulation reveals second-order effects, propagation patterns, and emergent shifts that are hard to infer from documents alone.

## Project Classification

- **Project Type:** Web application (SPA + API-backed workflow system)
- **Domain:** Scientific / computational simulation and AI-assisted analysis
- **Complexity:** Medium
- **Project Context:** Brownfield (existing system being extended and refined)

## Success Criteria

### User Success

- New users can complete their first end-to-end flow (upload -> graph -> simulation -> report) within 30 minutes without reading source code.
- Analysts can answer at least three "what-if" questions in one session using report and interaction views.
- Flow completion rate from `/` to first report generation reaches at least 60% in internal pilot environments.

### Business Success

- Internal adoption expands to at least three teams/use cases within eight weeks.
- Return behavior increases: at least 40% of projects trigger a second simulation run within 14 days.
- Each pilot captures at least one decision/recommendation influenced by MiroFish outputs.

### Technical Success

- Backend service health remains stable with `/health` continuously available during pilot operation windows.
- Phase-level execution is traceable through graph/simulation/report status endpoints and consistent logs.
- Job failures caused by configuration/environment/input issues are materially reduced through stronger preflight validation and clearer error messaging.

### Measurable Outcomes

- Time-to-first-report (TTFR): median <= 30 minutes.
- Report generation success rate: >= 85% for valid inputs.
- Simulation completion rate: >= 80% under default configuration.
- Critical escaped defects (P0/P1) after each pilot release: 0.

## Product Scope

### MVP - Minimum Viable Product

- Clear onboarding for the five-step workflow.
- Stronger validation and error feedback for input/env/config before long-running jobs.
- Consistent status/progress/log visibility from frontend to backend.
- Report output quality sufficient for first-cycle decision rehearsal.

### Growth Features (Post-MVP)

- Domain/use-case scenario templates.
- Multi-run scenario comparison (A/B style).
- Better observability and retry/recovery behavior for long-running simulations.

### Vision (Future)

- Decision-intelligence workbench where users create, replay, compare, and audit multiple future rehearsals on shared graph memory.
- Standardized scoring framework to compare scenario quality with objective metrics.

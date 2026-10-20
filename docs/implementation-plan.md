# MVP implementation plan

Status: proposed in the planning PR. Functional work is tracked as small GitHub issues and delivered one issue per pull request.

## Decision

Start with a single browser application using React, TypeScript, and Vite.

For the read-only MVP, data comes from typed fixtures behind adapter interfaces. Do not add a server until a real adapter requires server-side credentials, protected OAuth, or scheduled ingestion. This keeps the first increments visible and avoids designing an API before the projection contract is tested.

Recommended baseline:

- React + TypeScript + Vite;
- Vitest + Testing Library for unit/component tests;
- Playwright only when the first end-to-end navigation path exists;
- CSS owned by the application; no component framework in the first issue;
- runtime validation at external adapter boundaries.

## Why not adopt a full product first?

Existing systems cover important lower layers: GitHub Issues and pull requests cover coding work; Google Calendar and task systems own commitments; Linear, Notion, Atlassian and similar products cover project records; AI coding tools execute work. None is assumed to be the canonical cross-system model.

The control plane should therefore stay thin: adapters, coordination semantics, projection, recommendation, and navigation. Before each new integration, check whether an existing connector or supported product feature already supplies it.

Official references checked on 2026-10-20:

- GitHub Issues: https://docs.github.com/issues
- Linear agents: https://linear.app/agents
- Notion AI: https://www.notion.com/product/ai
- Atlassian Rovo: https://www.atlassian.com/software/rovo
- Google Calendar API: https://developers.google.com/calendar/api

## Vertical delivery sequence

Each slice should produce a visible behavior where practical. If visibility conflicts with keeping the issue reliably small, keep the issue small and let two or three consecutive slices combine into the next visible capability.

| Order | Slice | Observable result |
|---:|---|---|
| 1 | Runnable dashboard shell | Responsive grid of static placeholder panels |
| 2 | Project projection contract and fixture | Project placeholder becomes a rendered project list |
| 3 | Work-state summary | Counts and groups for ready, blocked, needs-user, autonomous, parked |
| 4 | Exact-context navigation | Project/thread cards open their configured source links |
| 5 | Needs-user queue | Short decisions are surfaced independently of whole projects |
| 6 | Dependency queue | Blocked work shows the missing prerequisite and its next action |
| 7 | Checkpoint view | A resumable checkpoint and next action can be inspected |
| 8 | Adapter boundary | Fixture loading goes through a replaceable projection adapter |
| 9 | Loading/error/stale states | Failure and freshness are explicit rather than silently misleading |
| 10 | First real read-only adapter | A configured public GitHub source replaces one fixture path |
| 11 | Conversational entry UI | Text command draft opens from a prominent “Talk to assistant” control |
| 12 | Voice-to-text enhancement | Supported browsers can dictate and edit the same command draft |
| 13 | Command gateway contract | Submission uses a configurable gateway with a safe local fake |
| 14 | Deterministic recommendation engine | Fixtures yield a best-fit action for a supplied time window |
| 15 | Landing recommendation | Top recommendation and alternatives appear without auto-execution |
| 16 | Calendar availability adapter | A provided availability projection supplies the current window |
| 17 | Private deployment/config boundary | Personal configuration is injected outside the public repository |
| 18 | MVP end-to-end acceptance scenario | All five canonical work states coexist in one tested flow |

## Issue sizing rule

An issue should normally change one behavior and one seam. Split it when it requires more than one of the following at once:

- a new external authorization flow;
- a new persistence model;
- a new integration;
- a new user-visible workflow;
- a broad refactor.

A slice is complete only when its acceptance criteria, automated checks, and review evidence are present.

## Deliberately deferred

- autonomous dispatch and agent runtime;
- writes back to external sources;
- universal task editing;
- background polling;
- production authentication;
- a generalized scheduler;
- ingestion/transcription pipelines;
- multi-user support.

These remain valid roadmap areas, but building them before the read-only projection proves useful would increase maintenance without validating the core hypothesis.

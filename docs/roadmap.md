# Roadmap

This roadmap is intentionally small. The project should prove the control model before building a large application.

## Phase 0 — concept

- [x] Define the problem: AI orchestration overhead and open loops.
- [x] Establish that the dashboard is a projection, not the source of truth.
- [x] Identify core entities: Project, Workstream, Thread, Checkpoint, Next Action, Dependency, Needs User, Autonomy.
- [x] Define a first real multi-thread acceptance test.
- [ ] Collect comparable production systems and reusable components.

## Phase 1 — schema prototype

- [ ] Define a minimal machine-readable schema.
- [ ] Represent 5–10 real workstreams from different domains.
- [ ] Test whether every active thread can be resumed from a checkpoint without rereading the full conversation.
- [ ] Refine the state model: autonomous / needs input / deep work / blocked / parked / complete.

## Phase 2 — read-only dashboard

- [ ] Build a projection over a few existing sources of truth.
- [ ] Show "Needs user now".
- [ ] Show blocked dependencies.
- [ ] Show resumable work.
- [ ] Show AI-autonomous work separately.


## Phase 2.5 — acquisition / ingestion

- [ ] Define a generic `Source -> Artifact` ingestion contract.
- [ ] Support at least a few representative source types: chat/thread references, webpages, PDFs, video/transcripts, and repository files.
- [ ] Preserve provenance: original source, retrieval time, transformations, and derived artifact identity.
- [ ] Normalize acquired material into reusable artifacts that can be passed between workstreams and AI workers.
- [ ] Represent failed or unavailable acquisition as an explicit dependency instead of requiring the user to remember the problem.
- [ ] Prefer existing production connectors/download/transcription infrastructure where available rather than rebuilding it.

## Phase 3 — continuation

- [ ] Add "Continue" actions.
- [ ] Dispatch work to an existing AI execution environment.
- [ ] Require every completed run to produce/update a checkpoint.
- [ ] Track source changes made by the run.

## Phase 4 — scheduler integration

- [ ] Connect priorities, deadlines, expected duration, and available time.
- [ ] Distinguish human-required work from autonomous AI work.
- [ ] Protect higher-priority real-world obligations from optional deep dives.

## Phase 5 — adapters and hardening

- [ ] Add adapters only where real use cases justify them.
- [ ] Add permissions and autonomy policies.
- [ ] Add freshness/staleness indicators.
- [ ] Add audit trail.
- [ ] Evaluate multi-user architecture if the project becomes a product.

## Explicit restraint

Do not build an agent runtime, project manager, or universal knowledge store merely because the project could.

Reuse production infrastructure whenever it already solves the lower layer adequately.

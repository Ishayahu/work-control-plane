# MVP implementation plan

Status: proposed in PR #1, pending human review. The runnable application does not exist yet. Deliver individual slices through reviewable PRs after the planning PR is approved.

## Working technical decision (2026-10-26)

Start with **Python + server-rendered HTML + HTMX**, as already recorded in `docs/architecture.md` on `main`. The **working first implementation candidate is Bottle + Jinja2 + HTMX**, with pytest as a test option. This is deliberately small and reversible; hosting, WSGI server, proxy and final dependency pins remain to be decided when implemented. Bottle was chosen for pedagogical minimalism, **not** because it has already been proven best for production.

Rationale:
- The user wants ordinary actions and state changes to update portions of the page without a full reload.
- The dashboard is primarily a view and navigator; a heavy client application is not currently justified.
- Running a Python application/server is acceptable. HTMX enhances rendered HTML; it does not replace the backend or an agent executor.
- Start with fictional fixtures; no real private connectors, external writes, or background agent machinery in the first slice.
- **Internet-facing release requires single-user authentication** even though no registration or multi-user management is planned. The working choice is **mTLS with client certificates on owner-controlled devices**, enforced by a reverse proxy; confirm the actual hosting, certificate issuance and revocation design before release. See `docs/architecture.md` §11 and issue #20.

## Development ownership: human-led logic, AI-assisted scaffolding

**Human developer owns** the domain model, architectural choices, business rules, integration semantics, acceptance criteria, and implementation of substantive logic. The assistant may provide explanations, focused code-review, debugging and paired incremental implementation.

**Coding agents may prepare**, only within the assigned issue:
- a minimal runnable project skeleton and configuration;
- responsive HTML templates and CSS (and narrowly scoped HTMX attributes);
- signatures, docstrings, type hints and explicit `NotImplementedError` / safe fixture-backed stubs *where a specific upcoming function has been approved*;
- mechanical documentation, formatting, non-domain boilerplate, and test harnesses.

**Agents must not** independently invent business rules, implement scheduling/recommendation decisions, connect private data, dispatch agents, or fill stubbed domain logic unless explicitly authorized in that issue. An attractive UI must not claim incomplete functions are working. The user reviews code and approves merging; agents must not merge.

Avoid generating a broad speculative architecture with dozens of empty functions. Build a small working vertical slice, then agree on the next seam. Include short annotations explaining HTMX to a developer who has not used it before.

## Framework portability and learning experiment (2026-10-27)

The application may start with Bottle and later **evaluate** Pyramid, Flask or another framework against observed needs. A migration is never mandatory or automatically scheduled. Treat changes of web framework as a practical learning/engineering experiment, not an end in themselves.

- Keep business/domain logic in ordinary Python functions or modules independent of Bottle's request/response globals, decorators and session machinery.
- Confine route definitions, HTTP adapters, authentication integration and HTMX response concerns to the thin web layer.
- Use **Jinja2** HTML templates (and fragment partials) rather than committing the UI to Bottle's SimpleTemplate syntax; Bottle and Pyramid both support Jinja2. Keep URLs and framework-specific helpers out of templates where practicable. HTMX itself does not render templates.
- Build only the files and interfaces required for the current vertical slice, *not* a speculative multi-directory skeleton.
- Before migration, identify a specific observed limitation and define equivalent end-to-end behavior and tests, including auth and CSRF protections. Compare time spent, refactoring effort, developer comprehension and actual outcomes; do not infer one framework's general superiority from non-equivalent prototypes.
- Migration still entails real cost: routing, request lifecycles, middleware, error handling, authentication, tests and deployment plumbing may change even when domain logic and templates remain stable.

## Agreed names for application responsibilities

Use the straightforward conceptual vocabulary **criteria / logic / connectors / web**. `criteria/` stores human-readable assessment definitions (not deployment settings); `logic/` handles assessment workflows and deterministic rules; `connectors/` provides provider integrations and persistence access; `web/` handles Bottle routes and Jinja2/HTMX responses. The names replace earlier generic `domain/services/adapters` terminology for code organization; they do not force four directories in the first slice.

## AI-first state assessment mechanism (architectural agreement; not first-slice implementation)

Domain vocabulary and evaluation criteria should be primarily **human-readable, versioned definitions**. Given a bounded and cited source context, an AI assessor assigns **typed values to separate criteria** (yes/no/unknown, categories, or defined-scale scores where warranted). A **deterministic Python policy/decision function** combines those values and independent explicit user choices to derive displayed work state and permissible actions.

- The human developer decides the criterion vocabulary, meanings, status precedence, uncertainty semantics and any weights/thresholds.
- The model assesses facts; it does not unilaterally set final status or grant authorization to send, spend, delete, or dispatch.
- Preserve evidence/source refs, timestamps, rule/prompt/model versions and human corrections; do not make a paid model call for every page render.
- Initial work-state fixture/filter issues (#3–#4) may use **provided structured assessments** and Python deterministic rules. Actual LLM classification arrives as a later, separately reviewed vertical slice after input contracts and storage are settled.

## Optional personal Telegram connector (issue #21)

Future integration: authorized personal-account Telegram messaging (read selected dialogs, prepare replies, send **only after explicit human approval** unless a later scoped policy is approved). Explore an MTProto user client or supported connector; a Bot API identity is insufficient for general personal dialogs and user-identity sending. Keep inbound message reading separate from outbound command execution, credentials/session isolated, delivery and approval audited, and background sync separate from Bottle. **No real Telegram client or connection in the first dashboard shell.**

## Why not adopt a full product first?

Existing systems cover lower layers: GitHub Issues/PRs cover coding work; Calendar and task systems own commitments; AI execution tools can perform work. The control plane should remain a thin, replaceable projection and coordination layer. Before any substantial new connector or subsystem, compare a supported existing integration or product against custom code.

Prior reuse-first review (2026-10-20) cited:
- GitHub Issues: https://docs.github.com/issues
- Google Calendar API: https://developers.google.com/calendar/api
- Linear agents: https://linear.app/agents
- Notion AI: https://www.notion.com/product/ai
- Atlassian Rovo: https://www.atlassian.com/software/rovo

These references are historical review inputs, not evidence of an updated compatibility check.

## Vertical delivery sequence (proposed, adjust before each slice)

Each slice should deliver a small, independently understandable outcome. Build **one issue per PR**. Domain-related slices are human-led or require explicit opt-in before delegation.

| Order | Slice | Ownership / observable result |
|---:|---|---|
| 1 | Runnable Bottle + Jinja2 dashboard shell | Agent-assisted: responsive Jinja2 page with fictional panels, manual run instructions, and a minimal tested HTMX HTML-fragment interaction; no business logic |
| 2 | First project projection contract and fixture | Human-led Python dataclass/typed domain model; agent may style template and write fixture harness |
| 3 | Work-state summary and filter | Human defines rules; HTMX updates filtered project list without full reload |
| 4 | Exact-context navigation | Agent can style safe links; human approves source reference semantics |
| 5 | Needs-user queue | Human-led domain projection with styled templates |
| 6 | Dependency queue | Human-led blocker semantics with styled cards |
| 7 | Checkpoint view | Human-led checkpoint contract, agent-assisted HTML details |
| 8 | Read-only adapter boundary | Human defines interface and validation; fixture-backed |
| 9 | Loading/error/stale states | Agent can implement presentation, human defines freshness and retries |
| 10 | Public GitHub read-only adapter | Human-led integration contract, safe server-side fetch; no private tokens |
| 11 | Conversational text entry | Agent-assisted accessible template and draft behavior |
| 12 | Voice-to-text enhancement | Optional browser-side enhancement; only if useful and supported |
| 13 | Command gateway contract | Human-led contract, safe fake endpoint, no execution |
| 14 | Deterministic recommendation logic | **Human implements business rules** with tests reviewed together |
| 15 | Landing recommendation | Agent-assisted templates over approved recommendation result |
| 16 | Calendar availability projection | Human-led interface, supplied fixture/JSON; no production OAuth |
| 17 | Public/private config boundary | Agent can prepare sanitized examples; human approves secret handling |
| 18 | Canonical end-to-end acceptance | Human decides success criteria; tested scenario with fictional data |

### HTMX learning contract

For the first interaction, demonstrate request method and URL (`hx-get`/`hx-post`), `hx-target`, and `hx-swap`, showing the exact Python handler and returned HTML fragment. One new concept at a time; do not assume prior HTMX knowledge. A small action should update the affected area without a full-page navigation. Ensure non-JavaScript fallback where sensible.

## Issue sizing and verification

- Restrict one PR to one behavior/seam. Avoid mixing a new external authorization flow, new persistence, new integration, and new UI workflow.
- Accept work only after independently examining the diff, running relevant Python checks/tests, and (for a visible UI) seeing desktop and mobile evidence.
- Tests for unimplemented domain functions should assert safe, explicitly documented behavior; do not claim that a stub is a finished feature.
- Track human time, agent time/cost, rework, and actual verified output. A faster agent run alone is not proof of better productivity.
- For experiments on Mail Bridge, apply the method separately there; do not silently change its workflow based on this dashboard plan.

## Deliberately deferred

Autonomous dispatch/executor, private integrations, full scheduling, automatic dependency resolution, external writes, generalized ingestion and multi-user support. These require independent decisions and explicit authorization.

**Authentication is not deferred beyond public deployment:** the fixture-based shell may be tested locally, but any Internet-exposed instance with real data or actions MUST be gated behind working and tested single-user **mTLS** authentication, HTTPS, and access-control/CSRF protections before going live. Implementation is a dedicated security/deployment issue (not an unreviewed addition to issue #2). The server framework choice and the gateway choice are independent.

## Implementation gate

Do not start issue #2 until PR #1 is reviewed/merged; the working first-slice stack is Bottle + Jinja2 + HTMX, subject to the human's final review of the implementation issue. The MVP scope and stack may be revised after the first functional prototype.

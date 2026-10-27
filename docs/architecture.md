# Architecture notes

## 1. Problem statement

AI systems increasingly perform long-running or multi-step work, but orchestration often remains human-driven.

The user must remember:

- which projects exist;
- which chat/session belongs to which project;
- where each thread stopped;
- what the next step is;
- whether the AI can continue alone;
- what is blocked;
- what requires a human decision;
- which source contains the authoritative state;
- which work deserves attention now.

This scales poorly because the number of open loops grows faster than the user's working memory.

## 2. Architectural boundary

Work Control Plane is not intended to become the canonical store for every project.

Instead:

```text
Domain systems / sources of truth
    GitHub
    Drive / Docs / Sheets
    Calendar
    task systems
    chats / agent workspaces
    databases
        |
        v
Adapters / Knowledge Gateway
        |
        v
Control metadata
        |
        v
Work Control Plane projection
        |
        +--> human actions
        +--> AI continuation
        +--> scheduler / dispatcher
```

The control plane may persist coordination metadata, but it should not duplicate domain state unnecessarily.

## 3. Minimal task-centered logical model (working simplification, 2026-10-27)

The earlier `Project / Workstream / Thread` three-tier distinction is being replaced in the **proposed shared Control Plane model** by a single, optionally nested **Task**. The owner has questioned the need for a separate `Project` or `Workstream` type: a large task can be decomposed into child tasks indefinitely. Existing source systems and repository names need not be renamed. References to "project" or "workstream" elsewhere in this document may still describe real-world source organization, not an additional mandatory logical entity.

### Task

A unit of work or intentional activity, large or small, identified by a stable ID and optionally a parent-task reference. A task can have children and can refer to its own canonical external store. **Each task, including a parent task, is completed against its own completion criterion.** Completion of every child task does not automatically complete the parent: assembly, integration, verification or other required outcomes may remain. Conversely, how incomplete child tasks affect evaluation of the parent's criterion depends on that criterion; do not invent a universal rule. A task's durable definition (completion condition, declared dependencies, explicit owner-imposed holds, consequential decisions/checkpoints, etc.) belongs in its canonical source. **Ephemeral operating labels** such as 'awaiting an answer in the current conversation' or 'resumable' may live in a local Control Plane projection/cache and need not be written back on every exchange. Losing the projection calls for a new audit rather than assuming it preserved transient state. Irreversible external-action approvals/operation records retain the separate durable recovery requirements described in §14.

**At creation, explicitly determine the task's completion criterion.** It may be deliberately absent (e.g. learning French purely for enjoyment), but not merely overlooked. When present, express an observable result/condition and use it in completion assessment; when absent, do not assume that an activity will ever enter a terminal completed state.

Distinguish **purpose** (why the task is valuable or which external goal it serves) from **completion criterion** (how to recognize its finish). A task can have intrinsic enjoyment value without an externally measurable goal. In otherwise comparable circumstances, a task without a defined outcome/external goal may deserve lower *default* scheduling priority than a task explicitly serving an important goal (English for an interview versus French for fun). This is **not** an unconditional priority rule: deadlines, responsibilities, explicit owner priorities and other factors may override it. No numeric weights or inference rules agreed yet.

Routine obligations need not be fabricated as evergreen tasks. For example, do not create "provide IT support" merely as a catch-all if there is no actionable work; create concrete repair/prevention tasks as needed. Do not create a special permanent "project" solely to group these.

### Task tags and categories (agreed minimal requirement, 2026-10-27)

A task may have **multiple tags** (e.g. `paid`, `unpaid`, `creative`, `translation`, `learning`). The dashboard must support filtering and grouping by tags **independently of the parent/child task hierarchy**. A single task may be both paid and creative; tagging must not force it into one exclusive category.

Initially represent this with a small task `tags` collection; **do not require separate Tag/Category domain entities or a taxonomy-management system** until real usage demonstrates a need. If some tags later describe mutually exclusive values along one dimension (e.g. paid vs unpaid), consider a controlled category/facet and validation at that point, without changing the basic recursive Task model.

**Inheritance is the default:** a child task's effective tags include the effective tags of its parent (transitively), unless explicitly overridden for that child. Support locally added tags and explicit exclusions of inherited tags; conceptually, `effective_tags(child) = (effective_tags(parent) ∪ added_tags(child)) − excluded_tags(child)`. Do **not** materialize inherited tags as independent local assignments by default, so a parent update propagates while a child's explicit exclusion remains effective. The override mechanism must work for multiple levels of nesting. Do not infer `unpaid` merely from absence of `paid`, and do not implicitly let mutually exclusive labels coexist: resolving controlled/exclusive tag dimensions remains a later schema decision. Whether tags directly affect priority is not yet decided.

### Reference

An identifier/link to the real source, including GitHub issue/repository/path, document, Google Sheet range, chat or agent session. The older `Thread` concept is normally just a **Reference**, not an independently managed entity. A task may have multiple references; references retain source provenance.

### Dependency

A directed dependency from a task onto another task or a condition (e.g. awaiting a reply, document or decision). The dependency is a relation, not necessarily a free-standing object with a separate life cycle. Distinguish unconfirmed/unknown conditions.

### Other aspects are data, not mandatory core entities

- **Checkpoint**: resumable state, decisions, changed artifacts, outstanding questions and next action.
- **Needs user**: assessed/derived criterion describing required human input, work or approval.
- **Autonomy policy**: separately enforced permission rules, not an AI-inferred grant.
- **Scheduling metadata**: deadlines, duration, effort/attention, urgency and priority criteria.
- **Source of truth**: task-owned reference to canonical storage; no compulsory shared physical file format.
- **AI assessment**: individual criterion values, evidence, timestamps and assessment version.

This is a conceptual model for discussion; physical Python classes, field constraints, relationship cardinality, completion behavior of parent tasks and source adapters should be decided through small real use cases rather than created wholesale now.

## 4. Work state: durable facts, computed blocks and transient dialogue state (revised, 2026-10-28)

**Do not maintain a manually updated persisted status enum for every conversation turn.** For ordinary unfinished work, **resumable / available for continuation** is the default after a source refresh, subject to verified dependencies and explicit holds. A status displayed on the dashboard is primarily a **projection**, not independent project-owned data.

Three separate mechanisms:

1. **Computed dependency blocker.** Declared task-to-task dependencies live in the canonical task source; program logic checks their present satisfaction. If a dependency is unfinished or unverified, show the appropriate blocked/unknown condition without writing a second 'blocked' status to the dependent task.
2. **Durable explicit hold.** If the owner explicitly says 'do not continue until X happens' (e.g. awaiting a response/permission from someone else, not readily expressible as an existing task dependency), save this block with its **reason and release condition** in the task's canonical source. Do not lose it when the Control Plane host is reset. The condition may be checked on later reviews, with the owner’s instruction remaining authoritative.
3. **Transient conversation state.** A question asked to the owner, an outstanding answer in the current conversation, a temporarily suspended session or available/resumable work can be tracked in the local dashboard database/cache. A response updates local state; do not commit to GitHub for each question/answer. The owner accepts that after loss of local state the system re-audits the task instead of recovering all transient dialog markers.

Optional cross-task **event inbox/index** in the dashboard may correlate observed events (e.g. an external reply or a confirmed completed task) with recorded waiting conditions and schedule a recheck. This is **not a second canonical task registry**. Polling/re-reading providers can recover replayable events after a cache loss. Where a one-off external event cannot be replayed, a purely volatile event log may miss it; solve that concrete durability case when encountered, rather than prematurely mandating a universal event store. Event receipt alone does not grant authority to resume a previously forbidden or side-effecting operation.

Completion of a parent task still depends **only on its own completion criterion**, not automatically on all children being completed. Distinguish 'no evidence of a blocker' from 'permission to execute'; approval policy and external-action safety gates are enforced separately. AI interpretation can assist only when unstructured source material is ambiguous; it is not needed for mechanically checking known dependencies or explicit owner instructions.

## 5. Scheduler integration

Project priority alone is insufficient.

The scheduler should reason over:

- deadlines;
- urgency;
- expected duration;
- revenue / obligation relevance;
- available time;
- attention cost;
- interruptibility;
- energy / deep-work requirements;
- dependencies;
- whether an AI can work autonomously while the human does something else.

A central design goal is that intellectually attractive work must not silently displace more important real-world obligations.


### Learning plans and readiness

A higher-level plan may aggregate several projects/workstreams that are executed in different chats. The first concrete example is a learning curriculum with multiple subjects.

The control plane should support a roll-up view that can derive:

- progress by subject;
- overall curriculum progress;
- the latest checkpoint for each subject;
- whether the subject is currently schedulable;
- prerequisites that must be resolved first.

This does not necessarily require a new source of truth or even a new core entity in the first schema. It may initially be a derived portfolio/program view over existing Projects and Workstreams.

A key distinction is **readiness**.

A workstream may be important and unfinished but still not be executable now because of a prerequisite such as:

- buying physical components;
- preparing equipment;
- installing or configuring software;
- obtaining a book/document;
- completing an earlier lesson;
- waiting for a real-world event.

These prerequisites should be represented as Dependencies and, when actionable, converted into scheduler-visible preparation tasks. When the dependency is resolved, the original workstream should automatically become eligible for scheduling again.


## 6. Interaction model: conversation first, dashboard second

The dashboard is **not** intended to replace conversational task management.

For many planning and coordination operations, free-form conversation is more efficient than GUI controls because the user can:

- add tasks in natural language;
- make arbitrary requests;
- refine or correct them immediately;
- ask contextual questions;
- combine several changes in one utterance;
- express exceptions that would be awkward to encode through forms.

The preferred interaction model is therefore:

```text
Free-form voice / text conversation
        |
        +--> add / change / clarify / plan / query
        |
        v
Control state + sources of truth
        |
        v
Dashboard
        |
        +--> eagle-eye overview
        +--> today's / current priorities
        +--> project and thread navigation
        +--> high-value shortcuts
        +--> immediate "continue" entry points
```

### Voice-first control

The interface should provide a prominent way to start a full conversational interaction by voice.

This does **not** necessarily imply a real-time voice-call UI. A speech-to-text flow that produces editable text before submission may be preferable because it preserves the advantages of text processing, reviewability, correction, logging, and structured extraction.

The important requirement is low-friction capture: the user should be able to speak a free-form instruction without navigating a task-management form first.

### Dashboard responsibilities

The dashboard's primary jobs are:

1. **Eagle-eye view** — show the current situation across projects, workstreams, blockers, readiness, and priorities.
2. **Fast navigation** — one click/tap should open the exact project, learning thread, chat, document, or execution context needed now.
3. **Contextual shortcuts** — expose a small number of actions that are genuinely faster than saying the same thing conversationally.

Example:

```text
Today

Kyrgyz
  ready
  [Open lesson]

Circuit theory
  blocked: buy experiment components
  [Open prerequisite]

Book project
  AI can continue
  [Continue]

[Talk to assistant]
```

A shortcut such as "Plan next week using my rules" is useful only if it reduces friction. If speaking the request is easier, the system should not force a dedicated button.


### Context-aware landing view

Opening the dashboard is itself a useful interaction signal.

By default, when the user opens the dashboard, the system may infer a lightweight intent:

> "Given my current context, what is the best thing to do now?"

If calendar access and scheduling metadata are available, the dashboard should immediately compute the current actionable window:

- current time;
- time until the next fixed calendar event;
- already planned work in that interval;
- workstream readiness and blockers;
- expected duration;
- priority and scheduling rules;
- whether the task requires human attention or can run autonomously;
- any other explicit user constraints available to the scheduler.

The landing view should then place a recommendation at the top, for example:

```text
You have 42 minutes free before the next calendar event.

Recommended now:
  Kyrgyz — 25–35 min
  ready; scheduled for today
  [Open lesson]

Alternatives:
  Logic — 20 min
  Review inbox — 10 min
```

This should not require the user to first ask "What should I do now?"

However, opening the dashboard is only a weak signal of intent, not authorization to start arbitrary work automatically. The default behavior should be **proactive recommendation and navigation**, not silent execution. The user must still be able to open the dashboard purely for overview, browse other projects, or use the conversational command surface.

This creates three layers of interaction:

1. **Proactive suggestion** — the system computes what fits now without being asked.
2. **Fast navigation** — one tap opens the selected work context.
3. **Conversation** — the user can override, refine, ask why, or request a different plan in free form.

### Design implication

The product should avoid becoming a traditional task manager with a dense control surface.

The conversational interface is the **command surface**.  
The dashboard is the **situational-awareness and navigation surface**.

## 7. Event loop

The long-term control loop may resemble:

```text
state changes
    |
    v
refresh project projection
    |
    v
classify open loops
    |
    +--> autonomous -> dispatch agent
    |
    +--> blocked -> track dependency
    |
    +--> needs user -> surface decision
    |
    +--> schedulable -> planner chooses slot
    |
    v
execution
    |
    v
checkpoint + source updates
    |
    +----> repeat
```

## 8. Thin-layer principle

Before implementing functionality, check whether it already exists in production tools.

Candidates include:

- ChatGPT Work / agent execution;
- Linear agents and recurring loops;
- Atlassian Rovo;
- Notion agents;
- Motion scheduling;
- GitHub;
- Google Workspace;
- existing MCP / connector ecosystems.

The control plane should own only the coordination semantics that are otherwise missing.


## 9. Acquisition / ingestion layer

A second major source of overhead is **getting material into a form that AI can actually work with**.

Examples include:

- moving information from one chat to another;
- extracting transcripts or subtitles from video;
- downloading source material from inconvenient interfaces;
- converting PDFs, webpages, audio, or exports into usable artifacts;
- preserving source metadata and provenance;
- handing the normalized artifact to another agent or workstream.

These steps are often mechanically necessary but do not require human judgment. They therefore belong in the system wherever they can be automated safely.

The intended flow is:

```text
Source URL / chat / video / PDF / repository
                    |
                    v
          Acquisition / ingestion
                    |
                    v
     normalized artifact + provenance
                    |
                    v
         Knowledge Gateway / adapters
                    |
                    v
          Work Control Plane
                    |
                    v
       analysis / writing / AI workers
```

The desired user experience is close to:

> "Use this source."

The system should then obtain the material, convert it when needed, preserve provenance, and make it available to the relevant workstream without forcing the user to perform the plumbing manually.

This layer should be conservative about permissions, access restrictions, credentials, and destructive operations. It should not bypass access controls or treat every source as legally or technically retrievable. When acquisition cannot be automated, that limitation should become an explicit dependency rather than an invisible burden on the user's memory.

A useful engineering heuristic for this project is:

> If an action is repeatedly required only to prepare material for the next intellectual step, and it does not require human judgment, it is a candidate for elimination through automation.

## 10. MVP implementation stack (working decision, 2026-10-26)

**Provisional choice:** Python backend with server-rendered HTML and HTMX for modest interactivity. **Initial trial:** Bottle for HTTP/routing with portable Jinja2 templates and HTMX HTML-fragment updates. This is a reversible first experiment, not a commitment to Bottle for the full product; possible trials of Pyramid or other frameworks remain open.

Why:

- The user expects button actions and status changes to update the relevant page fragment **without a full-page reload**.
- The initial dashboard is primarily overview, filtering, navigation, and a few high-value commands, not a rich client-side application.
- Server deployment is acceptable; avoiding a server is not itself a requirement.
- HTMX keeps interactive views close to Python HTML templates and avoids a separate Svelte/SPA build for now.

Development approach:

1. Begin with one small, annotated end-to-end HTMX interaction (HTTP request, Python handler, returned HTML fragment, target swap). Do not assume prior HTMX experience; explain relevant `hx-*` attributes when implementing.
2. Keep ordinary links/forms functional where practical; add HTMX progressively for inline refreshes, loading states, and actionable feedback.
3. Treat background data freshness separately from immediate action feedback. Polling, SSE, or another push mechanism should be chosen only if a concrete use case requires it.
4. Keep agent execution and external integrations outside the UI rendering layer; the Python application may delegate jobs to an executor/worker. HTMX does not itself execute background work.
5. Re-evaluate a richer frontend such as Svelte if actual interactions become significantly client-state-heavy; do not introduce it preemptively.

This is an implementation direction, not a claim that the architecture is fully decided.

## 11. Single-user authentication and public deployment requirement (2026-10-27)

**Mandatory product constraint:** The real dashboard will be reachable over the Internet, but access must be limited to its single owner. No public signup, self-service registration, social login, invitation flow, user directory, or role-management UI is required for the MVP. A public GitHub source repository does **not** imply a public dashboard.

### Proposed minimum, subject to host/proxy review

**Current access choice: mTLS using individual client certificates and private keys on the owner's controlled devices, preferably enforced at the HTTPS reverse proxy (e.g., Nginx if actually used).** The hosting/proxy is not yet verified. The user does not require access from unmanaged devices. This choice avoids adding a username/password login flow to Bottle, but the issuance and revocation system still needs to be designed.

- Require HTTPS on every public request. HTTP must not expose private content or accept credentials.
- Protect **all** HTML, HTMX endpoints, API routes, static assets containing private information, and command paths; default-deny, with no unintended unauthenticated bypass.
- Keep the Python process bound to loopback/private network where applicable so clients cannot bypass the proxy.
- Keep client **private keys** protected and out of source control, HTML, JS and logs. A client certificate without the matching private key cannot authenticate. Issue separate certificates per device when practical; define import, backup, expiration/renewal and revocation processes. Client and server TLS certificates serve different purposes.
- Reject missing, invalid, expired and revoked client certificates using an appropriate trust/revocation policy; monitor failed access attempts. Never treat concealment of a URL as authentication.
- Avoid state-changing `GET` routes. **Authenticated state-changing commands still need CSRF protection** (anti-CSRF token and/or verified origin with appropriate defense in depth), input validation, and explicit authorization boundaries.
- HTMX same-origin requests must remain authenticated. Tests must cover both full-page navigation and HTMX fragment/action endpoints.
- mTLS is device-key possession authentication, not a per-action approval mechanism. If a later requirement demands access from unmanaged devices or a distinct login/logout flow, reconsider a managed access gateway or server-side session solution rather than quietly weakening the chosen policy.

**Deployment gate:** local fixture-based development may proceed without production login; however, **no Internet-exposed deployment containing real/personal data or usable action endpoints is permitted until the protection is implemented and tested**. Track this as a distinct, reviewable security/deployment issue. No need for Django solely because the app requires a single login.

## 12. State interpretation: deterministic by default, AI only where needed (revised, 2026-10-28)

The owner rejected introducing an additional universal AI rubric for readiness when the relevant facts are already explicitly known. **Completion criteria are defined on Task creation**; no duplicate set of 'completion criteria' is needed. State derivation starts from:

- the task's own completion criterion and confirmed completion facts;
- explicit dependencies and their checked satisfaction;
- durable, explicitly imposed holds with reasons and release conditions in the canonical source;
- transient outstanding human questions and dialogue progress from the local Control Plane projection;
- independent authorizations and external action safety policy.

Ordinary unfinished work defaults to **resumable**, unless verified dependency status or an explicit hold prevents continuation. When local state is lost, re-read the canonical task source and dependencies and perform a fresh audit. The assistant may need to ask a question again; it must **not** infer a fresh permission to perform irreversible actions from a cleared cache.

**Deterministic code** resolves known dependencies, explicit flags and observed events. An LLM can optionally help extract meaning from unstructured documents or conversations and propose uncertain assessments, with provenance and owner correction, but is **not required** for routine status derivation and must never override an explicit hold or grant authorization.

Practical responsibility names remain **criteria / logic / connectors / web**:

- `criteria`: task completion criteria and any human-readable interpretations genuinely needed, not a mandatory AI-status-scoring system;
- `logic`: deterministic status derivation, dependency checks, optional interpretation, policy checks and event correlation;
- `connectors`: source-specific reads/writes, event sources and optional local storage;
- `web`: routes, rendered dashboard and HTMX interaction.

Do not generate modules for concepts without actual use in a vertical slice. The full list of display states, the local DB/cache implementation, event retention and review cadence remain implementation decisions.
## 13. Optional Telegram personal-account adapter (requirement, 2026-10-27)

The owner wants to **optionally connect their own Telegram account**, allowing the assistant to **read conversations** and, when authorized, **send messages under the owner's identity**. This is a future desired capability, not an active connection or permission to read/send now. Track in [issue #21](https://github.com/Ishayahu/work-control-plane/issues/21).

**Bot vs user distinction:** the Telegram Bot API operates as a bot and cannot generally read the owner's normal personal-account dialogs or send messages as that user. Investigate an authorized Telegram **MTProto user client** such as Telethon or TDLib, or a suitable maintained integration, and document limitations such as secret-chat coverage.

Separation of concerns:

- **Telegram adapter**: replaceable interface for authorized account connection, selected chat/message reads, provenance identifiers, and sending requests. Keep Telegram-specific session handling outside Bottle/Jinja2 and outside domain-status criteria.
- **Inbound ingestion**: explicitly scope chats, retrieval, refresh frequency and retention. Incoming messages are untrusted data, not instructions authorizing agent actions.
- **Outbound command/approval**: construct a draft and show exact recipient, message text and reply target for the user's approval **before** sending. Merely connecting or reading Telegram does not grant send authority. More autonomous sending would need a separate, narrowly scoped human-approved policy.
- **Execution/audit**: design a durable outbox/idempotency strategy to mitigate duplicated sends; record authorization, attempt and resulting Telegram message reference, and expose uncertain delivery outcomes.
- **Secrets**: user-client API credentials, login challenges and Telegram authorization/session material are sensitive and must remain outside the public repository or HTML/AI prompts; plan backup/revocation and account-compromise response.
- **Runtime**: a long-running MTProto listener or periodic synchronizer, if selected, should be isolated from the Bottle request lifecycle. First decide whether bounded read-on-demand is enough.

The website's **mTLS client certificate** authenticates the owner to Work Control Plane; it does not authenticate to Telegram and does not imply authorization to send a specific message. The first Bottle shell (#2) must not be expanded into a Telegram integration prematurely.

## 14. Project-owned state and recovery of uncertain external actions (working decision, 2026-10-27)

**Durable task facts and significant instructions belong to that task's single canonical source**: definition, declared dependencies, completion criteria, explicit owner-imposed holds with reason/release condition, consequential decisions/checkpoints and relevant history. A transient 'awaiting the user's answer' marker or 'resumable' label is **not** necessarily canonical task state. Local dashboard storage can retain such markers, recent assessments/events and caches and may be lost; its loss triggers re-evaluation. Do not update a GitHub repository merely because the assistant asked a routine question or received an answer. Existing learning projects already have GitHub context; do not create companion stores for them without reason. No mandatory SQLite/PostgreSQL requirement is imposed solely by this conceptual decision. **The distinct durable operation records below are still required for recovery of side-effecting external actions.**

For an external action that might have side effects (e.g. sending a Telegram message), use a small **project-owned durable operation record** when recovery matters:

1. Record the exact instruction and authorization, target, parameters, and unique operation identifier **before** attempting it (`pending` or equivalent).
2. Execute through the appropriate connector.
3. On confirmed provider success, record the external result reference and mark `completed`; don't confuse an HTTP/UI reply with provider confirmation.
4. After a crash or lost response, a record that lacks `completed` means **outcome unknown**, not automatically `failed` or `not executed`.
5. Query the provider, where possible, for evidence that the operation occurred. Confirm `completed` if reliably identified; if not observed, present 'apparently not completed' with evidence/limits; if ambiguity remains, explicitly mark it **uncertain**.
6. **Do not silently retry irreversible/external actions.** Ask the owner to verify or approve a retry. Provider-level deduplication/idempotency may reduce risk where supported but cannot be assumed.

The user-facing wording should distinguish: `confirmed_completed`, `apparently_not_completed`, `outcome_unknown`. Absence of a matching outgoing Telegram message is not necessarily proof of non-delivery (history may be incomplete/deleted; identical messages may be ambiguous). Avoid inventing a guarantee of exactly-once delivery.

Retain operation approvals and the relevant audit history with the corresponding project (or its project-owned companion store) if durable recovery is required. If a particular external action truly cannot be recovered without separate infrastructure, demonstrate that failure case before introducing a central mandatory operation database. **Loss of the Control Plane host should not erase canonical project decisions or automatically cause repeated sends.**

## 15. Connector contract: common logical model, native project storage (agreed, 2026-10-27)

**A single normalized interface, not a mandated universal physical file format.** Each project preserves its own canonical data representation (e.g. GitHub Markdown/issues, Google Drive documents, Sheets, or another native store). A source-specific connector translates the project's fields and evidence into the shared in-memory structures consumed by Control Plane logic. No requirement to retrofit every existing project with a common JSON/YAML file.

- **Read:** discover/resolve project source references and project-scoped work state, normalize the subset needed by logic, and preserve source identifiers, timestamps/provenance and unknown/missing values.
- **Write:** when a change has been explicitly approved and the target source is writable, map the requested change back into that project's native representation. Do not silently modify a different source or assume every connector supports writing. Handle version/conflict checks appropriate to each source.
- **Capabilities:** connectors may be read-only or provide a limited range of mutations; surface unsupported operations explicitly.
- **No loss of source-specific detail:** normalized views are deliberately partial; do not rewrite or discard fields the shared model does not understand.
- **Project-local authority:** durable task definitions, explicit holds, consequential decisions and essential checkpoints/history remain at the canonical task location. Operational conversation flags and derived statuses may be cached in Control Plane and reconstructed or re-audited as needed; no unnecessary status write-back after each exchange.
- **Architecture boundary:** generic logic consumes a stable application-facing contract, without hardcoding GitHub/Sheets data formats. The contract should emerge from real vertical slices rather than speculative interfaces.

### Discovery via the existing context router (working decision, 2026-10-27)

Use the already-existing **`Ishayahu/main-ai`** context repository as the discovery/navigation root instead of creating another canonical task/project list in Work Control Plane:

- `INDEX.md` routes natural-language intents to relevant context; it is not automatically a complete machine-readable list of individual tasks.
- `initiatives/REGISTRY.md` lists registered initiatives and pointers; `links/SOURCES.md` and linked cards may resolve additional canonical systems. Do not read dated snapshot statuses in `projects/Pnnn.md` as current truth.
- Registered top-level work can use its existing identifier (e.g. `P031`, `central-asia`) with an appropriate namespace when uniqueness requires one. Load concrete child tasks from their canonical sources (e.g. Google Sheets, GitHub Issues); don't replicate every leaf in the router.
- **One logical task has exactly one canonical state owner at a time.** The record pointed to by the router is authoritative for task status, completion criterion, progress, blockers, checkpoints and task metadata. A task may include references to chats, documents, code or calendar entries, but these are supporting sources/artifacts, **not parallel copies of the task state**.
- The canonical source reference itself normally determines the connector (for example, GitHub or Google Sheets); do not duplicate a provider selector as mandatory task metadata. Resolve the source using a registered connector, and report unsupported or ambiguous link types explicitly.
- The in-memory Control Plane projection may cache task records, but such caches are disposable/reconstructible. Avoid bidirectional status synchronization and duplicate authoritative records.
- Before applying this design in code, check that the existing registry covers the root activities needed for the dashboard; don't presume it is exhaustive or machine-readable without adaptation.

### Existing records and canonical routing: no migration or deletion requirement (corrected, 2026-10-28)

The dashboard should **not require moving, deleting, reconciling or synchronizing** legacy copies of task records. The existing Google Sheets planner and all `main-ai` content remain **unchanged** during architecture work, and do not need to be cleaned up when the dashboard is introduced. A future explicit, separately authorized cleanup is optional, not a prerequisite.

For each registered root Task, the context registry should ultimately resolve to **one designated canonical state location** (e.g. `Ishayahu/work-control-plane` for P031), not one link *total*: incidental links to related artifacts may remain. A valid state change goes **only to that canonical location** through its connector. Any older state copies in Sheets or elsewhere are out of scope and are not consulted to reconcile the canonical status. The task source link tells the system which connector to use; duplicate provider selectors are unnecessary.

As of 2026-10-28, `Ishayahu/main-ai/initiatives/REGISTRY.md` explicitly routes **P031** to `Ishayahu/work-control-plane` (`task.yaml`), **P032** to `Ishayahu/book-of-control` (`task.yaml`), and **P021** to the existing Google Sheets planner. These three entries now each expose one canonical-source link; corresponding historical card files and original Sheets entries remain unchanged. The `main-ai` index, snapshot README and source navigation were updated to reflect the exceptions. Other legacy registry rows may still contain multiple navigational links, so treat their ownership resolution as an independent later task; do not automatically infer or migrate it. Data was copied into the two GitHub `task.yaml` files with source provenance and old planner milestones marked historical, without altering Google Sheets.

### Normalized read/write contract (to define with concrete examples)

The shared model is **only the shape of the information returned to logic**, based on the already-agreed recursive Task design: stable source-backed ID, title, optional parent, explicit completion-criterion state (defined / intentionally none / unknown), task status/uncertainty, effective inherited tags and overrides, dependencies, checkpoints and source references. This is **not** a mandate to rewrite all source documents in a common storage format. Resolve the connector from the task's one canonical reference; it knows how to read and apply specifically approved changes to that source's native structure (with conflict detection and explicit read-only restrictions). Other references are supporting context, not alternative write destinations. AI-derived dashboard evaluations never silently override human decisions or authorize external changes. The exact Python fields and read/write method signatures can be refined while implementing a real task example; do not reopen settled model decisions without a concrete reason.

## 16. Open architectural questions

- Where should control metadata live?
- How are checkpoints produced and validated?
- How should thread identity work across vendors?
- How stale may a projection become before it is misleading?
- Which changes are event-driven vs polled?
- How are conflicting updates reconciled?
- How should permissions and autonomy policies compose?
- What is the minimal useful scheduler integration?
- How can the system remain useful when one vendor is unavailable?
- How should private personal configuration be separated from a public generic core?

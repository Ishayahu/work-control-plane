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

## 3. Core entities

### Project

A durable goal or responsibility.

Possible fields:

- id
- name
- objective
- priority
- status
- source references
- scheduling policy

### Workstream

A coherent branch of work inside a project.

Examples:

- literature review;
- implementation;
- data collection;
- writing;
- debugging.

### Thread

A concrete execution context.

Examples:

- a ChatGPT conversation;
- a coding-agent session;
- a research run;
- a GitHub issue;
- a document-writing session.

A thread is important because one project may have several simultaneous conversations or agents.

### Checkpoint

A compact resumable state.

A checkpoint should answer:

- what has been completed;
- what is currently believed / decided;
- what artifacts or sources changed;
- what remains open;
- what next action is recommended;
- whether human input is required.

The checkpoint is a handoff protocol between sessions.

### Next Action

The next meaningful unit of work, not merely the next UI click.

### Dependency

A condition that prevents continuation.

Examples:

- missing document;
- awaited reply;
- unavailable credential;
- unresolved architectural decision;
- calendar event.

### Needs User

A first-class distinction.

Suggested states:

- `no` — AI may continue;
- `short_input` — a small choice or answer is needed;
- `deep_work` — joint reasoning is required;
- `approval` — action is ready but requires authorization.

### Autonomy Policy

Defines actions the AI may take without asking.

Example:

```yaml
autonomy:
  research: true
  draft: true
  edit_project_files: true
  create_new_external_resources: ask
  delete_data: ask
  spend_money: never
  external_communication: ask
```

### Source of Truth

Pointers, not copies.

Examples:

- Git repository/path;
- Google Sheet ID/range;
- document URL;
- issue ID;
- database record;
- agent/chat/thread reference.

## 4. Work states

A dashboard should distinguish at least:

- **Ready / resumable** — can continue now.
- **AI can continue** — no user involvement needed.
- **Needs short input** — a small decision blocks progress.
- **Needs deep work** — human reasoning time is required.
- **Blocked externally** — waiting for a dependency.
- **Parked** — intentionally paused.
- **Complete** — no open loop.

This is more useful than a single generic "in progress" state.

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

## 12. AI-assessed criteria and deterministic status derivation (working architecture, 2026-10-27)

**Separate semantic interpretation from formal state derivation.** In this AI-first control plane, the model should **not be the final arbiter of a project's status or authority to act**.

Pipeline:

1. Collect bounded, traceable **facts** from source adapters: messages, events, issues, checkpoints, explicit user instructions.
2. Load **human-readable domain definitions** (for example Markdown criteria for readiness, blocked dependencies, sufficiency of context, human decisions) and an agreed output schema.
3. Ask an AI model to **assess individual criteria**, returning validated structured values and supporting source references. Values need not be numeric: use enums/booleans/unknown where meaningful; numeric scores/weights only when useful and their scale is defined.
4. Apply **deterministic, reviewable Python rules** to the assessment and separately stored explicit user choices/policies to derive the displayed state, including precedence among states.
5. Preserve criterion values, evidence, model/version/rule-version, timestamp and uncertainty. Show the explanation and let a human correct assessments. Re-evaluate on meaningful source changes or explicit refresh, not necessarily on each page request.

Illustrative **hypothetical** assessment (schema not fixed yet):

```json
{
  "context_sufficient": "yes",
  "next_step_defined": "yes",
  "blocking_dependency": "no",
  "requires_user_decision": "no",
  "assessment_confidence": 0.91
}
```

The program can conclude **technically ready** when relevant criteria are affirmative and no blockers are known. However, *technical readiness* is separate from *owner intent* (e.g. deliberately parked), *authorization* (whether AI may perform the next action), and *data freshness*. A model inference must never grant spending, deleting, externally messaging or other protected authority.

Practical module boundaries (agreed naming for application code, 2026-10-27):

- **Criteria (`criteria/`)**: human-readable meanings and assessment rubrics, plus the declared criterion vocabulary. This is deliberately named **criteria**, not `domain/` and not generic runtime settings.
- **Logic (`logic/`)**: collect/assess facts, validate structured AI answers, apply deterministic status derivation and authorization policy, coordinate commands. Formerly called `services/`.
- **Connectors (`connectors/`)**: exchange data with external providers, AI APIs, Telegram, and local/remote persistence. Formerly called `adapters/`.
- **Web (`web/`)**: Bottle routing, request/response integration, Jinja2 presentation and HTMX partials (roughly controller + view). Keep substantive logic outside this layer.
- **Runtime configuration**: separate from criteria and never assume secrets belong in the public repository.

These labels describe responsibilities; create modules/directories only when a concrete implementation slice needs them.

Do not prematurely create directories for every conceptual responsibility. Decide the actual schema, statuses, precedence and override semantics in a separate small, human-led slice before implementation.

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

## 14. Open architectural questions

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

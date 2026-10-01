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

## 6. Event loop

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

## 7. Thin-layer principle

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


## 8. Acquisition / ingestion layer

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

## 9. Open architectural questions

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

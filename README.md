# Work Control Plane

A personal control plane for coordinating many parallel human+AI workstreams without forcing the human to keep their state, dependencies, and next actions in working memory.

The project starts from a practical problem: modern AI assistants can perform substantial work, but the human still has to orchestrate many separate chats, projects, tools, and unfinished threads. As the number of useful AI workflows grows, the administrative overhead of managing them can become a new bottleneck.

Work Control Plane aims to move that orchestration burden out of the user's head.

## Core idea

The system should answer, at a glance:

- What workstreams are currently open?
- Which ones can an AI continue autonomously?
- Which ones are blocked, and by what?
- Which ones need a human decision?
- What is the next meaningful action?
- Which source of truth contains the actual project state?
- What should be worked on now, given priorities, deadlines, available time, and attention budget?

The dashboard is **a projection, not a source of truth**.

Project/domain state remains in the systems that already own it: GitHub, Google Drive/Docs/Sheets, calendars, task systems, ChatGPT/other AI workspaces, databases, etc. The control plane stores or derives only the metadata needed to coordinate work across those systems.

## Why this exists

Typical multi-project AI work creates many open loops:

1. A learning thread is paused and should be resumed later.
2. A research thread is blocked on obtaining a transcript or source.
3. Another AI task can continue without human involvement.
4. A project needs a short human decision before it can proceed.
5. A scheduler must protect paid work, deadlines, family obligations, or other real-world constraints from being displaced by interesting but non-urgent AI work.

Doing all of this manually turns the human into the project manager of their AI assistants.

The desired model is different:

> The human manages intent, priorities, authority, and genuine decision points.  
> The system manages checkpoints, dependencies, context recovery, continuation, and routine orchestration.

## Initial domain model

The first MVP will likely revolve around:

- **Project** — a long-lived goal or area of work.
- **Workstream** — a coherent branch of work within a project.
- **Thread** — a concrete conversational or execution context (chat, agent run, coding session, research session, etc.).
- **Checkpoint** — a compact, structured statement of the current state.
- **Next Action** — the next meaningful step.
- **Dependency** — something that must happen before the next step.
- **Needs User** — whether a human decision or input is actually required.
- **Autonomy Policy** — what the AI may do without asking.
- **Source of Truth** — pointers to the systems that own the underlying state.
- **Scheduling / Attention Metadata** — urgency, time budget, deadlines, interruptibility, and similar constraints.

See [docs/architecture.md](docs/architecture.md).

## Design principles

1. **Dashboard != database of reality.**  
   The dashboard is a materialized view / projection over existing systems.

2. **Every work session should leave a checkpoint.**  
   Resuming work should not require reconstructing the whole chat history.

3. **Minimize human hand-holding.**  
   An AI should stop only at genuine decision boundaries, not after every intermediate step.

4. **Open loops must be explicit.**  
   Paused, blocked, autonomous, and human-dependent work should be distinguishable.

5. **Parallelism without cognitive overload.**  
   Several workstreams may progress simultaneously while the user sees only the few that need attention.

6. **Execution engines are replaceable.**  
   The project should reuse existing agents, schedulers, coding tools, search tools, and integrations where possible instead of rebuilding them.

7. **No vendor lock-in at the control-model level.**  
   ChatGPT, Linear, Notion, Atlassian, GitHub, Google Workspace, or future tools should be adapters, not the conceptual core.

8. **Real-world scheduling matters.**  
   Interesting AI work must not automatically outrank paid work, deadlines, sleep, family obligations, or other constraints.

9. **Conversation is the primary control interface; the dashboard is the overview and navigator.**  
   Free-form voice/text interaction is better for adding tasks, changing plans, asking arbitrary questions, and refining intent. The dashboard should provide an eagle-eye view, quick entry into the right project/thread, and a small number of high-value shortcuts rather than forcing management through forms and buttons.

## First acceptance test

A useful MVP should be able to represent a situation like this without the user keeping it all in memory:

- one learning thread is simply parked and resumable;
- one research thread is blocked on obtaining a missing source;
- one writing task can continue autonomously;
- another workstream needs a short human decision;
- the scheduler can say which of these should happen now.

If the user still has to remember those states and dependencies manually, the MVP has failed.

See [docs/use-cases.md](docs/use-cases.md).

## Relationship to adjacent systems

Work Control Plane is intentionally thinner than a full project-management suite or agent framework.

It may sit above:

- AI execution environments (ChatGPT Work, coding agents, research agents);
- project systems (Linear, Jira, Notion, GitHub Issues);
- knowledge gateways and retrieval systems;
- calendars and task schedulers;
- Google Drive/Docs/Sheets;
- email and messaging integrations.

The project should first evaluate what can be reused from production systems and implement only the missing coordination layer.

## Status

Early concept / architecture stage.

The first goal is not to build a large application. It is to validate the minimal control model and prove that it can reduce orchestration overhead on real parallel work.

## License

Licensed under the **Apache License 2.0**.

The short version: commercial use, modification, redistribution, and proprietary products built on top are allowed, while the license provides explicit patent terms and requires preservation of license/attribution notices.

Why Apache-2.0 was chosen, and how it differs from MIT/GPL/no-license, is documented in [docs/licensing.md](docs/licensing.md).

## Contributing

At this stage, useful contributions include:

- examples of similar production systems;
- critiques of the control model;
- real multi-agent / multi-project workflows that break the proposed model;
- simpler alternatives;
- schemas and adapter ideas;
- prototypes that reduce the human orchestration burden.

The project is deliberately public: if someone else solves the problem well, that is a useful outcome too.

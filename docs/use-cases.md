# Use cases and acceptance criteria

## Use case 1 — parked learning thread

A user studies a topic over multiple short sessions.

The system should preserve:

- where the lesson stopped;
- the last concept mastered;
- the next exercise or concept;
- whether anything must be prepared before resuming.

The user should not have to remember the chat name or reconstruct the lesson history.

**Acceptance criterion:** one action resumes at the correct conceptual checkpoint.

## Use case 2 — research blocked on a source

A research/audit thread cannot proceed until a transcript, PDF, dataset, or other source is acquired.

The system should show:

- the workstream;
- the missing dependency;
- the action that will become possible once it is resolved;
- whether the dependency can be resolved autonomously.

**Acceptance criterion:** the research does not occupy working memory while blocked, but becomes visible again when actionable.

## Use case 3 — autonomous continuation

A writing, coding, or research task has enough context for an AI to continue.

The system should classify it separately from work needing human attention.

**Acceptance criterion:** the human can delegate/continue it without reopening and re-explaining the original conversation.

## Use case 4 — short human decision

A workstream is blocked on a small choice.

The dashboard should surface the actual decision rather than the whole project.

Example:

```text
Project X
Needs user: 2-minute decision
Question: choose A or B
Consequence: ...
```

**Acceptance criterion:** the user can clear several small blockers without entering each project's full context.

## Use case 5 — multiple chats in one project

A single project has independent research, implementation, and writing chats.

The system must not equate "project" with "chat".

**Acceptance criterion:** all threads are visible under one project and each has its own checkpoint and next action.

## Use case 6 — attention-aware scheduling

The user has:

- urgent paid work;
- an interesting research thread;
- a parked learning thread;
- an autonomous AI job.

The scheduler should distinguish work that requires the human from work an AI can execute in parallel.

**Acceptance criterion:** the system does not recommend deep optional research merely because it is engaging when higher-priority obligations are still unmet.

## MVP acceptance test

The MVP should handle all of these simultaneously:

| Workstream | State | Expected behavior |
| --- | --- | --- |
| Learning | Parked | Remember checkpoint; do not nag |
| Research | Blocked on source | Show dependency, hide from active attention until actionable |
| Writing | AI can continue | Offer/dispatch autonomous continuation |
| Design | Needs short input | Surface only the decision |
| Paid/urgent work | Human + high priority | Protect time in scheduler |

If the user still has to remember the state or dependency of each thread, the MVP is not solving the target problem.

## Non-goals for the first version

- replacing GitHub, Drive, Linear, Notion, or task managers;
- building a new general-purpose agent runtime;
- duplicating every artifact into a central database;
- building a large enterprise PM suite;
- predicting priorities from opaque AI intuition without explicit constraints;
- forcing every project into a single execution tool.

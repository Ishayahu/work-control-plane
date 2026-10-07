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


## Use case 7 — one learning plan, many subject chats

A long-term learning plan may contain several subjects studied in separate chats or tools: for example logic, music theory, circuit theory, languages, or other topics.

The user should not have to remember:

- which chat contains each subject;
- where each subject stopped;
- how far the overall curriculum has progressed;
- which subjects are ready to continue immediately;
- which subjects are blocked on a prerequisite;
- whether a prerequisite is intellectual (read a chapter), logistical (buy a component), or environmental (set up software / equipment).

The control plane should aggregate progress upward from subject-level checkpoints into the broader learning plan.

Example:

```text
Learning plan

Logic
  state: ready
  checkpoint: validity and counterexamples
  next: continue lesson

Music theory
  state: ready
  checkpoint: ...
  next: ...

Circuit theory
  state: blocked
  dependency: buy components for physical experiment
  after dependency: run experiment and continue
```

The scheduler should treat "ready to study" and "blocked on preparation" differently. A blocked subject should not occupy working memory, but its prerequisite should appear in the appropriate actionable queue (for example, a shopping/preparation task). Once the prerequisite is resolved, the subject becomes schedulable again.

**Acceptance criterion:** the user can open the learning-plan view and immediately see overall progress, which subjects can be studied now, and what concrete prerequisites are preventing the others from progressing, without remembering the individual chats.


## Use case 8 — voice-first planning with dashboard navigation

The user primarily manages tasks and plans through free-form conversation, often by voice.

Typical interactions include:

- "Add this to the plan."
- "Move this to next week."
- "What can I work on now?"
- "Plan next week using my usual rules."
- "I need to buy something before I can continue circuit theory."
- arbitrary corrections and exceptions that were not anticipated by the UI designer.

The dashboard should not require the user to translate these requests into forms or manual field edits.

At the same time, conversation alone is poor at persistent situational awareness and navigation. The dashboard should therefore show the current plan and provide direct entry into the relevant work context.

Example: if today's plan says "Kyrgyz", tapping that item should open the exact Kyrgyz learning thread rather than require the user to search through chats.

A prominent "Talk to assistant" control should start a full free-form voice/text interaction. Speech-to-text with editable/transformed text is acceptable and may be preferable to a live voice session.

**Acceptance criterion:** routine planning can be performed conversationally, while the dashboard gives immediate visual overview and one-step navigation to the exact work context without duplicating the same management operations as a form-heavy UI.


## Use case 9 — opening the dashboard during a free calendar window

The user opens the dashboard without asking a question.

The system can see that the calendar is free for a bounded period before the next commitment. It should treat this as enough context to compute a default recommendation.

Example:

```text
Free until 15:40 (38 minutes)

Best fit now:
  Kyrgyz
  expected: 25–30 min
  ready
  [Open]

Also fits:
  Logic — 20 min
  Small admin task — 10 min
```

The recommendation should be derived from the same rules used by the scheduler, not from a separate dashboard-specific heuristic.

Blocked tasks should not be proposed as immediately executable. A task that requires buying equipment, acquiring a source, or resolving another dependency should instead surface its prerequisite when that prerequisite itself fits the current context.

The dashboard should not silently start work merely because it was opened. Opening implies "recommend intelligently", not "execute without confirmation".

**Acceptance criterion:** if the user opens the dashboard during a free calendar interval, the system immediately shows a sensible best-fit next activity and direct entry into it without requiring an extra "what should I do?" request.

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

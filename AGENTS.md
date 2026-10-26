# Instructions for coding agents

Read `README.md`, `docs/architecture.md`, `docs/implementation-plan.md`, and the assigned GitHub issue before changing code.

## Delivery contract

- Work on exactly one assigned issue per pull request; preserve a small reversible diff.
- Follow the issue's acceptance criteria. Do not implement later features early.
- Link the issue in the PR body (`Closes #<number>` for an actual implementation PR).
- Report tests and commands actually run; report failures, missing checks, and any unfinished stubs.
- Attach a desktop and narrow-screen screenshot for visible UI changes when feasible.
- **Never merge your own PR.** The human developer reviews and approves it.

## Division of responsibility

- **Human developer owns:** architecture and framework decisions, domain models, business rules, scheduler/recommendation logic, permission policies, real integration behavior, and approval of implementation.
- **Agent-assigned work, when explicitly scoped:** small Python web-project scaffolding, responsive HTML/CSS, template partials, minimal HTMX wiring, docstrings/signatures/type annotations for approved interfaces, fixtures, test harnesses, formatting, documentation.
- Do not autonomously implement domain logic, build broad abstractions, add dependencies, pick a new frontend stack, create private connectors, or dispatch AI jobs.
- Domain signatures/stubs must be agreed for a concrete slice. Stubs must clearly indicate incompleteness and must not falsely appear to work.
- Explain the relevant `hx-*` attributes and server fragment contract when introducing HTMX; the human developer is new to HTMX.
- For features requiring real implementation choices, pause at the defined boundary instead of inventing business rules.

## Technical baseline

- Provisional MVP stack: **Python, server-rendered HTML, HTMX, CSS**.
- Do not use React, TypeScript, Vite or introduce a client SPA unless the human later revises the decision.
- Python web framework, template tooling, and tests remain undecided until the first implementation slice.
- Dynamic UI updates should replace a targeted HTML fragment without a full page reload. HTMX is UI plumbing, not the agent executor.
- Preserve keyboard accessibility and useful ordinary HTML semantics. Avoid unnecessary JavaScript.
- Keep domain logic independent from route handlers/templates, and source adapters independent from domain state.
- Do not pre-build a large empty object model. Design only what the current slice requires.

## Product, privacy and authorization boundaries

- Dashboard = projection / navigation surface, not a second system of record.
- Keep this public repository generic. Do not commit private personal files, tokens, credentials, calendar exports, or private repository contents.
- Use fictional fixtures until an issue explicitly permits a real adapter.
- Opening the dashboard must not silently start external work. No automatic external writes, agent runs or spending.
- Conversations remain the main command surface; the dashboard is overview and navigation.
- Check for existing production solutions and connectors before building substantial integrations.

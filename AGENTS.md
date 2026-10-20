# Instructions for coding agents

Read `README.md`, `docs/architecture.md`, and the assigned GitHub issue before changing code.

## Delivery contract

- Work on exactly one issue per pull request.
- Keep the change small enough to review and revert independently.
- Use the issue's acceptance criteria as the scope boundary; do not implement later issues early.
- Link the issue in the PR body with `Closes #<number>`.
- For visible UI changes, include a screenshot or short recording in the PR.
- Run and report the relevant checks. Do not hide failing checks.
- Do not merge the PR. Leave it ready for human review.

## Product boundaries

- The dashboard is a projection, not the source of truth.
- Keep the public repository generic. Never commit Ishayahu's personal data, private repository contents, tokens, credentials, calendar data, or exports.
- Use fixtures and adapter interfaces until an issue explicitly introduces a real integration.
- Conversation is the command surface; the dashboard is the overview and navigation surface.
- Opening the dashboard may recommend work, but must not silently execute it.
- Do not add an agent runtime, general project manager, or universal knowledge store.

## Engineering defaults

- Prefer the smallest implementation that satisfies the issue.
- Keep domain types independent from React components and data-source adapters.
- Validate data at adapter boundaries.
- Add dependencies only when their value is clear in the PR description.
- Preserve accessibility and keyboard use.
- Avoid speculative abstractions; extract only after a second real use.

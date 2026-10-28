# MVP-01: local runnable dashboard shell

This intentionally small **Bottle + Jinja2 + HTMX** application is a display-only first slice. The **only working UI action** is selecting one of four task-state tabs: the browser requests server-rendered HTML and HTMX replaces the corresponding fragment **without reloading the page**. No task logic, provider/LLM calls, messaging, voice, financial computation, calendar sync, personal data, persistence or external writes are included. All other controls are visibly disabled.

## Start on your own computer

From `src/`:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:8080/ . The server deliberately binds to **127.0.0.1 only**. **Never expose this unauthenticated preview to the Internet.** Production deployment must pass the separately planned HTTPS/mTLS authentication gate.

To see conditional Inbox overflow with **fictional messages only**, open:
- http://127.0.0.1:8080/?demo_inbox=0
- http://127.0.0.1:8080/?demo_inbox=3
- http://127.0.0.1:8080/?demo_inbox=20

## How the HTMX demonstration works

The four tabs are ordinary hyperlinks. Without HTMX, clicking loads `/?view=ai` as a full page. With HTMX, each tab declares:

- `hx-get="/task-view/ai"` — issue GET to the Bottle route;
- `hx-target="#task-switcher"` — target the selected task panel;
- `hx-swap="outerHTML"` — replace the old panel node with the **Jinja2 HTML fragment** returned by the route.

The Bottle handler calls `_task_switcher.html`, not a Bottle-specific inline template or a JSON API. A pinned HTMX script is loaded from the jsDelivr CDN, with SRI. Network access to that CDN is needed for enhanced interactions; the ordinary links remain usable without it.

## Run tests

```sh
python -m pip install pytest
python -m pytest -q tests
python -m compileall -q app.py
```

Mobile baseline: 390 × 844 viewport; static outer page and internally-scrollable overflowing Inbox/answer/task panels. Smaller viewports, zoom and open keyboard may require scrolling as an accessibility fallback. On desktop, the task-state categories are simultaneously visible.

## Next

After review and merging this slice, implement a typed task projection and source adapters. Prioritize backend model routing/failover (issue #23) and read-only e-mail/Telegram inbox ingestion followed by explicit triage (reply, create/link task, mark handled), with no auto-conversion of messages into tasks. Real outbound replies need the owner's authorization or pre-approved scoped rule.

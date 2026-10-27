# Application source placeholder

The initial application will be introduced only after review of the planning PR (#1).

Working first-slice stack: **Bottle + Jinja2 + HTMX** for server-rendered HTML and targeted fragment updates; no React/Vite scaffold. Keep substantive Python logic independent from Bottle route handlers so another framework (Pyramid/Flask) can be compared later, but do not create unused abstraction directories.

The first implementation slice should produce a truly runnable responsive HTML shell with fictional data, plus **one minimal HTMX request returning a fragment from a Python handler**. Other domain functionality may remain expressly unimplemented.

Domain rules, project contracts, scheduler logic and real integrations are reserved for human-led incremental development. Do not pre-generate a speculative function hierarchy.

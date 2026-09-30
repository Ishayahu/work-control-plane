# Why Apache License 2.0

This repository uses the **Apache License, Version 2.0**.

This document explains the project-level rationale. It is not legal advice; the LICENSE file is authoritative.

## What Apache-2.0 allows

In practical terms, Apache-2.0 is a permissive open-source license.

It allows people and companies to:

- use the software privately;
- use it commercially;
- modify it;
- distribute original or modified versions;
- include it in proprietary products;
- sublicense/distribute derivative works under additional terms, provided the Apache-2.0 obligations for the covered code are respected.

This matches an important goal of the project: if another person or company implements the idea well, that can still be a positive outcome.

## What it requires

When covered code is redistributed, Apache-2.0 generally requires preservation of:

- the license text;
- relevant copyright / attribution notices;
- notices that modified files were changed;
- applicable NOTICE information, if the project later includes a NOTICE file.

The license does **not** grant rights to project trademarks.

## Why Apache-2.0 instead of no license

A public GitHub repository is visible, but visibility alone does not give everyone broad permission to reuse the code.

Without an explicit license, normal copyright restrictions still apply.

That would conflict with the project's stated intent: experimentation, reuse, forks, alternative implementations, and potentially someone else solving the problem.

## Why Apache-2.0 instead of MIT

MIT would also be a reasonable choice and is simpler.

Apache-2.0 was preferred mainly because it contains an **explicit patent license from contributors** for patent claims necessarily infringed by their contributions, plus a patent-retaliation clause.

For a project that may eventually include orchestration protocols, adapters, agent-control mechanisms, and contributions from multiple developers or companies, that explicit patent language is useful additional clarity.

MIT is shorter; Apache-2.0 is more explicit.

## Why not GPL / AGPL by default

GPL and AGPL are strong copyleft licenses.

They are useful when a project specifically wants derivative implementations to remain open under compatible copyleft terms.

That is not the current objective here.

The project intentionally leaves room for:

- proprietary integrations;
- hosted commercial services;
- enterprise extensions;
- private deployments;
- companies adopting the open core without being forced to open unrelated proprietary components.

Apache-2.0 makes that adoption easier.

If the strategic goal later changes from "maximize useful implementation and reuse" to "require downstream derivatives to remain open", the licensing strategy can be reconsidered for future code. Already released versions, however, remain available under the license under which they were published.

## Does Apache-2.0 prevent monetization?

No.

Possible commercial models remain available, including:

- hosted SaaS;
- managed deployments;
- support and consulting;
- enterprise connectors;
- team / organization features;
- proprietary services around the open core;
- dual-licensed future components where legally possible.

The license deliberately does not try to make the raw idea itself the competitive moat.

If the project becomes commercially valuable, likely moats are more likely to come from execution, UX, integrations, operational know-how, hosted infrastructure, ecosystem, and adoption.

## Public core vs private configuration

The intended boundary is:

### Public

- generic architecture;
- schemas;
- adapters;
- orchestration logic;
- generic UI;
- documentation;
- reusable code.

### Private

- personal project data;
- private chat/thread identifiers;
- credentials and secrets;
- private source mappings;
- personal schedules;
- private deployment configuration;
- confidential business data.

This separation is useful even apart from licensing: it forces the architecture to distinguish reusable product logic from one user's personal environment.

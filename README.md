# Planning Center API skill

A Claude skill with a complete, verified reference for the [Planning Center Online](https://api.planningcenteronline.com/docs) REST API: People, Services, Groups, Check-Ins, Giving, Calendar, Registrations, Publishing, Webhooks, API and Current. It covers every resource's endpoints, attributes, filters and payloads, plus auth (PAT/OAuth), pagination, rate limits and webhooks, and ships a small Python client (`scripts/pco_client.py`).

Claude uses it automatically whenever a task touches Planning Center.

## Install

### Claude Code

Run these two commands inside Claude Code:

```
/plugin marketplace add https://github.com/FBCSpringdale/planning-center-api.git
/plugin install planning-center-api@fbc-springdale
```

Or from your shell:

```sh
claude plugin marketplace add https://github.com/FBCSpringdale/planning-center-api.git
claude plugin install planning-center-api@fbc-springdale
```

To get updates, run `/plugin marketplace update fbc-springdale`, or turn on auto-update for `fbc-springdale` under **Marketplaces** in `/plugin`.

### Other agents (Cursor, Codex, Copilot, etc.)

```sh
npx skills add FBCSpringdale/planning-center-api
```

## Contents

- `skills/planning-center-api/SKILL.md`: cross-cutting rules and the product map
- `skills/planning-center-api/references/`: one file per product
- `skills/planning-center-api/scripts/pco_client.py`: Python client and CLI
- `skills/planning-center-api/evals/`: eval cases
- `tests/test_pco_client.py`: offline checks for the client (`python3 tests/test_pco_client.py`)

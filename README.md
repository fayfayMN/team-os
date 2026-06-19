# 🧭 Team OS

**👉 Open the app: https://fayfaymn-team-os-app-ttgvcb.streamlit.app/**

A **lightweight team collaboration system** — for startups, small businesses, and
school clubs that are running without structure. It makes explicit the four things
that quietly break teams:

1. **Who decides?** — decision rights
2. **Who does the work vs. who's just informed?** — RACI
3. **How do we talk and stay aligned?** — the charter
4. **What did we actually decide, and why?** — an immutable decision log

It's the **RUN** stage that complements the **TeamUp** app (FORM a team) and
**Clearwork** (PROVE who contributed). It is a *separate, independent app* — it
does not touch or depend on the TeamUp project.

## Run locally

```bash
cd team-os
pip install -r requirements.txt
streamlit run app.py
```

Click **Load demo team** on the home page to see the RACI health check flag a
deliberately broken setup.

## What's in v1

| Page | What it does |
|------|--------------|
| **Home** | Team name, totals, demo data |
| **Charter** | Members + living charter (mission, values, decision/check-in/quiet/credit rules), exportable |
| **RACI** | Workstreams × members grid with a deterministic health check (no owner, split accountability, overloaded hero, uninvolved member) |
| **Decision Log** | Append-only record of decisions with reasoning; supersede instead of edit; exportable |
| **Health Pulse + Coach** | Anonymous pulse (results hidden until enough responses); a coach that recommends one EOS-native practice at a time, foundation-first |
| **Level 10 Meeting** | EOS weekly rhythm: 60-min agenda, IDS issues list (raise → discuss → solve/drop), resolved issues auto-log to Decision Log |
| **Rocks** | 3–7 quarterly priorities, one owner each, binary (done / not done), guardrails on count |
| **Scorecard** | 5–15 weekly numbers with owner + goal, weekly entry, 6-week history table |
| **Export Hub** | Push data to Google Sheets (CSV), Notion/Docs (Markdown), or Slack/Discord/Teams (formatted messages) — no API keys |

## Design principles

- **Deterministic & explainable** — all checks are pure Python; no API key, no cost,
  nothing to hallucinate. Data persists to `teamos_state.json`.
- **Schema-versioned entities** so future upgrades (more layers, more fields) are cheap.
- **Backend is swappable** — JSON now; Google Sheets / SQLite later behind the same
  `store.py` API.

See [TEAM_OS_PLAN.md](TEAM_OS_PLAN.md) for the full layered design and roadmap
(communication norms, cadence engine, health pulse + coach, board, roadmap,
connector sync, audience starter packs).

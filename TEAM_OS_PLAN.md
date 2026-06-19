# Team OS — Lightweight Team Collaboration System

> A **separate, independent app**. It complements TeamUp (FORM) and Clearwork
> (PROOF) but lives in its own folder and has no dependency on either — so the
> established TeamUp app is never at risk.

```
   FORM            →            RUN  (Team OS — this app)        →      PROOF
  TeamUp                  charter · decisions · comms ·                Clearwork
 match+kickoff           work · cadence · health                      contribution
                                                                      resume card
        └──────────────── reputation flows back ───────────────────────┘
```

## Core thesis

Unhealthy team dynamics in startups, small businesses, and school clubs trace to
**four ambiguities**. Team OS makes each explicit and keeps it alive through cadence:

1. **Who decides?** → decision rights (RACI/DACI) + immutable decision log
2. **Who does vs. who's just informed?** → RACI matrix per workstream
3. **How/where do we talk?** → communication charter + meeting hygiene
4. **Are we healthy?** → anonymous pulse → health dashboard → "adopt this next" coach

Lightweight is the wedge: not another Jira. The differentiator is that the app
**diagnoses and recommends the next healthy practice**, rather than dumping 30
features on a new team.

## Operating doctrine (locked)

These decisions are settled and constrain every future module:

1. **Target the willing-but-unaware leader; protect members from the unwilling one.**
   Most "closed-minded" leaders are overwhelmed, not malicious — a tool helps them by
   externalizing feedback and acting as a mirror. A genuinely unwilling/toxic leader
   cannot be fixed by software; for them, the goal shifts to *protecting team members*
   via **real anonymity** and **member-owned, append-only records** that surface truth
   regardless of leadership.
2. **Borrow EOS, not Scrum.** A weekly issue-resolution rhythm (Level 10 / IDS), a
   simple scorecard, and a single-owner accountability chart are small-business-native.
   Sprints and heavy ceremony are not. The coach recommends EOS practices.
3. **Don't rebuild daily ops.** Cash, invoices, tasks, scheduling are well-served by
   incumbents (and the user's existing Small Business plugin). Team OS owns only the
   **structural + health layer** no task tracker touches: ownership clarity, decision
   discipline, and team health.
4. **Coach, don't feature-dump.** The diagnostic that says "adopt *this one* practice
   next" is the moat. The board/roadmap are the *least* important things to build —
   incumbents win those.

## Design principles

- **Deterministic, explainable core.** RACI checks, prioritization, and health
  scoring are pure-Python weighted rules — free, instant, no hallucination.
- **LLM is optional and bounded.** Only for: meeting notes → action items, retro
  summary, charter draft, health narrative. Never the core logic.
- **Backend stays invisible.** `store.py` hides storage (JSON now → Google Sheets
  / SQLite later).
- **Config/schema-driven modules.** Each layer = a JSON schema + one Streamlit
  page. `schema_version` on every record makes migrations cheap.

## The layered model

A team adopts layers in order of maturity — never all at once.

| Layer | Frame | Proven practice | Lightweight feature | Status |
|---|---|---|---|---|
| 0. Foundation | — | Charter, values, working agreement | Living charter | **v1 ✅** |
| 1. Leadership & decisions | Leadership | RACI/DACI, decision rights, psychological safety | RACI matrix + immutable Decision Log | **v1 ✅** |
| EOS Level 10 | Leadership | Weekly meeting, IDS issue resolution | Level 10 page + Issues List | **v2 ✅** |
| EOS Rocks | Direction | Quarterly priorities, binary accountability | Rocks page | **v2 ✅** |
| EOS Scorecard | Operations | Weekly measurables, early-warning numbers | Scorecard page | **v2 ✅** |
| 2. Communication | Communication | Async-default, channel charter, meeting hygiene, SBI feedback, retros | Comms charter + meeting template (decision/owner/due) | v3 |
| 3. Project management | Project mgmt | Kanban, WIP limits, Definition of Done, blocker escalation | Now/Doing/Done board + blocker routing | v4 (low priority — incumbents win this) |
| 4. Product management | Product mgmt | Now-Next-Later roadmap, RICE/ICE/MoSCoW | Roadmap board + deterministic prioritization scorer | v4 |
| 5. Operations | Operation layer | Onboarding/offboarding runbooks, capacity/load | Onboarding checklist + load view | v3 |
| ✶ Cross-cutting | Healthy dynamics | Team health checks (Edmondson; Project Aristotle) | Anonymous pulse → coach → EOS next-practice | **v1.5 ✅** |

## Entity model (versioned, append-only where it matters)

```
Team (name) ─┬── Member (name, role)
             ├── Workstream
             ├── RACI  raci[workstream_id][member_id] = R|A|C|I
             ├── Decision   (append-only; supersede, never edit)
             └── Charter (mission, values, decision/checkin/quiet/credit rules)
```

Future entities: Ritual (cadence), Pulse (health), Document (runbooks).

## Audience starter packs (future — config files, not code)

- **School clubs / student teams** — volunteers, churn, credit fights.
- **Startups** — OKRs, fast decisions, Now-Next-Later roadmap.
- **Small businesses** — recurring operations/runbooks, role clarity.

## Roadmap

**v1 — shipped in this scaffold**
- Living Charter (members + mission/values/rules, exportable).
- RACI matrix with deterministic health check (no owner / split accountability /
  overloaded hero / uninvolved member).
- Immutable Decision Log (supersede, never edit; exportable).
- Local JSON persistence; opt-in flawed demo team.

**v1.5 — shipped: the centerpiece**
- Anonymous Health Pulse (no author stored; results suppressed below MIN_RESPONSES).
- Deterministic Coach: foundation-first maturity ladder (charter → RACI → decisions →
  pulse → health dimensions), recommends one EOS-native practice at a time.
- Leadership-openness detector: chronically low "feedback changes nothing" is named
  honestly as a leadership problem, not papered over with more process.

**v2 — shipped: EOS operating rhythm**
- EOS Level 10 page: 60-min agenda cheatsheet, IDS issues list (raise → discuss →
  solve/drop), resolved issues auto-log to Decision Log with owner.
- Quarterly Rocks (3–7 priorities, one owner, binary done/not-done, guardrails on count).
- Scorecard (5–15 weekly numbers, owner + goal, weekly entry, 6-week history, guardrails).
- Coach updated: new "Run your first Level 10" stage between decisions and pulse, plus
  secondary nudges for missing Rocks/Scorecard and off-track Rocks.
- Demo team now includes sample issues, rocks (one off-track), and scorecard metrics.

**v2.5 — shipped: Export Hub (universal bridge)**
- Export Hub page with three tabs: Google Sheets/Excel (CSV), Notion/Docs/Wiki
  (Markdown), Slack/Discord/Teams (formatted messages).
- 13 export generators: RACI, decisions, issues, rocks, scorecard as CSV + Markdown;
  Level 10 summary, pulse reminder, and full team snapshot as chat messages.
- No API keys — copy/paste/download. Team OS stays the source of truth; external
  tools are the display layer.

**v3 — Operate++**
- API-based Notion sync (create/update pages directly).
- Discord webhook for automated pulse reminders and Level 10 summaries.
- SQLite/Sheets backend; simple auth; three audience starter packs.
- Pulse trends over time (cycles, not just one pool).

**v3 — Connect & prove**
- Lightweight board (Now/Doing/Done, WIP limits, blocker escalation).
- Roadmap + prioritization scorer.
- MCP connector sync (Slack / Notion / Google Calendar / Jira).
- Decision log + contributions feed Clearwork → reputation back to TeamUp.

**v4 — Polish**
- Optional LLM helpers (meeting notes→actions, retro summary, charter draft, health narrative).

## Deferred decisions (not blocking v1)
- First specialized audience pack (currently generic).
- When to move off JSON to a real DB (driven by multi-team / auth need).

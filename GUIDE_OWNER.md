# Team OS — Owner / Admin Guide

You're the person setting this up for your team. That might mean you're a
founder, a club president, a team lead, or just the person who cares enough
to build structure. This guide walks you through setup, the weekly rhythm,
and how to read the signals the app gives you.

---

## First-time setup (30 minutes)

Do these in order. The app's Coach (Health Pulse page) will tell you the same
thing — it won't let you skip ahead because each step depends on the last.

### Step 1 — Name your team (Home page)

Open the app and type your team or org name on the Home page. This label
appears on all exports.

### Step 2 — Write the Charter (Charter page)

This is the most important 15 minutes you'll spend. Fill in:

- **Members** — add everyone on the team with their name and role. You can
  always add or remove people later, but start with who's here now.
- **Mission** — one or two sentences everyone would agree to. Not a vision
  statement — what are we *actually here to do*?
- **Values** — one per line. Keep it to 3–5. These should be behavioral
  ("ask early", "credit the work") not aspirational ("excellence").
- **How we decide** — the default is good for most teams: "The Accountable
  owner decides after 10 minutes of disagreement, and we move on." Change
  it if you have a better rule; don't leave it blank.
- **Check-ins** — when does the team sync? Weekly is the minimum.
- **If someone goes quiet** — this is your free-rider defense. Agree now
  what happens, so it's not personal when it happens.
- **Credit** — how contributions are recognized. This prevents the loudest
  person claiming everything at the end.

Click **Save charter**. Then copy the exported Markdown and paste it into
wherever your team lives (Slack channel, Discord, Notion, Google Doc) and
have everyone react or acknowledge it.

> **Why this matters:** A charter is the document you point back to when
> things drift. "We agreed to this" is far more powerful than "I think we
> should." Without it, every conflict is a negotiation from scratch.

### Step 3 — Set up RACI (RACI page)

RACI answers the question that silently breaks most teams: *who actually
owns this?*

1. **Add workstreams** — these are the areas of work your team owns. For a
   startup: maybe "Product", "Sales", "Ops". For a club: "Build",
   "Outreach", "Logistics". Don't go granular — 3–6 broad areas.
2. **Fill the grid** — for each workstream × member, assign:
   - **A (Accountable)** — owns the outcome. **Exactly one per workstream.**
     This is the most important rule: if two people are Accountable, no one is.
   - **R (Responsible)** — does the work. Can be multiple people.
   - **C (Consulted)** — gives input before a decision.
   - **I (Informed)** — told after it's done.
   - Blank = not involved.
3. **Run the health check** — the app will immediately flag:
   - A workstream with no Accountable owner (🔴 error)
   - A workstream with two Accountable owners (🔴 error)
   - No one Responsible (🟡 warning)
   - A person Accountable for too many things — hero risk (🟡 warning)
   - A member with no role on anything — free-rider drift (🟡 warning)

Fix the red errors before moving on. The yellow warnings are worth a
conversation but not blockers.

> **Why this matters:** Ambiguous ownership is the #1 driver of both
> free-riders ("I thought someone else was doing it") and burnt-out heroes
> ("I guess I'll just do everything"). RACI makes it explicit.

### Step 4 — Log your first decision (Decision Log page)

Log at least one real decision. It doesn't have to be big — "We'll meet
on Tuesdays at 5pm" counts. The point is to start the habit of recording
*what was decided and why*, so the team has a shared record.

Decisions are append-only on purpose. If you reverse a call later, you log
a *new* decision that supersedes the old one. You never edit history.

### Step 5 — Set up the weekly rhythm (Level 10 + Rocks + Scorecard)

These three pages are the EOS (Entrepreneurial Operating System) operating
rhythm — the most proven lightweight model for small teams:

**Level 10 Meeting** — schedule a weekly meeting, same day and time. The
page has a 60-minute agenda cheatsheet:
- Good news (5 min)
- Scorecard review (5 min) — are the numbers on/off track?
- Rock review (5 min) — are priorities on/off track?
- Headlines (5 min) — quick FYIs, no discussion
- To-do review (5 min) — did last week's to-dos get done?
- **IDS (30 min)** — the heart: work the Issues List. Identify the real
  problem, Discuss briefly, Solve with a decision + owner.
- Conclude (5 min) — recap decisions and rate the meeting 1–10.

You don't have to follow this rigidly from day one. But having *a* weekly
rhythm is non-negotiable for a functioning team.

**Rocks** — at the start of each quarter, agree on 3–7 priorities. Each
Rock has one owner and is binary: done or not done. "Off track" isn't a
punishment — it's a signal to IDS at the Level 10.

**Scorecard** — pick 5–15 weekly numbers the whole team can see. Revenue,
hours logged, issues closed, outreach posts — whatever matters for your
team. Enter actuals each week. The point is early warning: a number going
off track *before* it's a crisis.

### Step 6 — Run the first Health Pulse (Health Pulse page)

Share the Health Pulse link with your team. Each person answers 8 questions
(1–5 scale) anonymously. **No name is attached to any response, ever.**
Results stay hidden until at least 3 people respond — this is the anonymity
guarantee that makes honest answers safe.

Once you have enough responses, the **Coach** tab tells you:
- Your team's maturity stage (Forming → Operating → Healthy / At risk)
- The single next practice to adopt
- Which dimensions are low

**Read the Coach recommendation honestly.** If "leadership openness" is the
lowest score, the bottleneck is you, not the team. That's uncomfortable but
it's the most valuable signal the app can give you.

---

## The weekly routine (15 minutes of admin)

Once set up, your weekly work as the owner is:

| When | What | Where | Time |
|------|------|-------|------|
| Before the Level 10 | Enter this week's Scorecard actuals | Scorecard page | 5 min |
| During the Level 10 | Work the Issues List (IDS) | Level 10 page | part of the meeting |
| After the Level 10 | Post the Level 10 summary to your channel | Export Hub → Chat → Level 10 summary | 2 min |
| Monthly or biweekly | Share the Health Pulse link | Export Hub → Chat → Pulse reminder | 1 min |
| Quarterly | Review and set new Rocks | Rocks page | 15 min |

---

## How to read the Coach

The Coach on the Health Pulse page recommends one thing at a time, in
order of maturity. It will never tell you to do step 5 before step 2.

| Coach says | What it means | What to do |
|------------|---------------|------------|
| "Write your charter" | No shared agreement exists | Go to Charter page |
| "Fix ownership (RACI)" | Structural errors in the RACI | Fix red errors on RACI page |
| "Start a weekly issues + decisions rhythm" | No decisions recorded yet | Log decisions; start Level 10s |
| "Run your first Level 10" | Decisions exist but no issues resolved | Hold a Level 10 meeting with IDS |
| "Run an anonymous pulse" | Structure is solid, no health signal yet | Share the pulse with the team |
| "Improve [dimension]" | A specific dimension scored low | Follow the practice it recommends |
| "Leadership openness — not process" | Feedback chronically changes nothing | The hardest one. See below. |
| "Healthy — keep the cadence" | Everything is working | Maintain the rhythm |

**On the "leadership openness" warning:** This fires when "when I give
feedback, something changes" scores very low. The app is telling you that
adding more structure won't help — the team doesn't believe their input
matters. The only fix is visible action: pick the lowest-scoring dimension,
make *one* change the team asked for, and say so publicly. If this score
doesn't improve over repeated cycles, the problem is deeper than any tool
can solve.

---

## Exporting to your tools (Export Hub page)

Team OS is the source of truth. Your other tools are the display layer.

**Google Sheets / Excel:**
Download CSV files for RACI, Decision Log, Issues, Rocks, or Scorecard.
Import into Google Sheets (File → Import → Upload) or open directly in Excel.

**Notion / Google Docs / Wiki:**
Select what to export, copy the Markdown, paste into Notion (it auto-converts)
or Google Docs. Use "Everything" for a full team snapshot.

**Slack / Discord / Microsoft Teams:**
Copy a pre-formatted message — Level 10 summary, Pulse reminder, or Team
snapshot — and paste it into your channel.

---

## Tips from experience

- **Don't set up everything on day one.** The Coach exists precisely so you
  adopt one practice at a time. Charter → RACI → first decisions → first
  Level 10 → first pulse. That's weeks of work, not an afternoon.
- **The RACI is worth fighting for.** When someone says "we don't need this,"
  it usually means they don't want to give up implicit control. That's the
  exact dynamic RACI is designed to surface.
- **Log decisions even when they feel small.** "We'll use Canva for social
  posts" sounds trivial until someone redesigns everything in Figma next
  month and claims no one ever decided.
- **Don't run the pulse too often.** Monthly or biweekly is right. Weekly
  is survey fatigue; quarterly is too late to catch problems.
- **Take the pulse yourself.** Your answers are anonymous too. If you're
  honest, you might learn something about your own blind spots.

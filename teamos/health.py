"""Team health — anonymous pulse + the coach.

This is the centerpiece of Team OS. Two deterministic, explainable pieces:

1. **Pulse** — a short anonymous check across the dimensions that research links
   to team effectiveness. Real anonymity is enforced by MIN_RESPONSES: nothing
   is shown until enough responses exist that no individual can be identified.

2. **Coach** — looks at the team's *structure* (charter? RACI? decisions logged?)
   and its *pulse*, and recommends **one** next practice, drawn from EOS
   (Entrepreneurial Operating System) — the lightweight, small-business-native
   model — in order of maturity. Coach-first, not feature-dump: one move at a time.

No LLM: every recommendation is a transparent rule with a stated "why".
"""

from __future__ import annotations

from statistics import mean
from typing import Dict, List, Optional

# Suppress all results below this many responses, so no single response can be
# singled out. The core anonymity guarantee.
MIN_RESPONSES = 3

# 1..5 Likert. A dimension averaging below this is treated as a problem.
LOW = 3.0
SERIOUS = 2.5

# Each question maps to a dimension. Dimensions mirror the four ambiguities plus
# the research-backed drivers (psychological safety — Edmondson / Project
# Aristotle; the rest from the EOS "people / accountability / data" components).
QUESTIONS: List[Dict] = [
    {"id": "safety",        "dimension": "Psychological safety",
     "text": "I can raise problems, mistakes, or tough issues without fear of blame."},
    {"id": "role_clarity",  "dimension": "Role clarity",
     "text": "I know what I'm accountable for, and what everyone else owns."},
    {"id": "decisions",     "dimension": "Decision speed",
     "text": "We make decisions and move on, instead of stalling or revisiting endlessly."},
    {"id": "workload",      "dimension": "Workload fairness",
     "text": "Work is fairly shared — no one is silently carrying the team or coasting."},
    {"id": "direction",     "dimension": "Direction",
     "text": "I know our top priorities right now and how my work connects to them."},
    {"id": "communication", "dimension": "Communication",
     "text": "Information I need reaches me in time, in a place I can find it."},
    {"id": "credit",        "dimension": "Credit",
     "text": "Contributions are recognized fairly — credit follows the work."},
    # The willing-vs-unwilling-leader detector. If feedback chronically changes
    # nothing, the problem is openness at the top, which no process can fix.
    {"id": "openness",      "dimension": "Leadership openness",
     "text": "When I give honest feedback, something actually changes."},
]

DIMENSION_OF = {q["id"]: q["dimension"] for q in QUESTIONS}


# ── Aggregation (anonymity-aware) ─────────────────────────────────────────────

def aggregate(responses: List) -> Optional[Dict]:
    """Return per-dimension averages, or None if below the anonymity threshold."""
    if len(responses) < MIN_RESPONSES:
        return None
    dims: Dict[str, List[int]] = {q["id"]: [] for q in QUESTIONS}
    for r in responses:
        for qid, val in r.scores.items():
            if qid in dims:
                dims[qid].append(int(val))
    per_dim = {qid: round(mean(vals), 2) for qid, vals in dims.items() if vals}
    overall = round(mean(per_dim.values()), 2) if per_dim else 0.0
    return {"per_dimension": per_dim, "overall": overall, "n": len(responses)}


# ── The coach ─────────────────────────────────────────────────────────────────

def _rec(title: str, why: str, practice: str, severity: str = "warn") -> Dict:
    return {"title": title, "why": why, "practice": practice, "severity": severity}


def coach(state: Dict) -> Dict:
    """Recommend the single next practice.

    state = {
        has_charter: bool,
        raci_errors: int,          # structural RACI errors
        has_workstreams: bool,
        decisions_count: int,
        responses_count: int,
        pulse: dict | None,        # output of aggregate()
    }

    Returns {primary: rec|None, also: [str], maturity: str}.
    Foundational gaps come first — there's no point measuring health before the
    basics (ownership, a record of decisions) exist.
    """
    pulse = state.get("pulse")
    also: List[str] = []

    # ── Stage 1: foundations must exist before anything else ──────────────────
    if not state.get("has_charter"):
        return {"primary": _rec(
            "Write your charter",
            "There's no shared agreement on mission, values, and how you work. "
            "Everything else drifts without it.",
            "EOS calls this the Vision: agree what you're here to do and the few "
            "rules for how you operate. Start on the Charter page.",
            "error"), "also": also, "maturity": "Forming"}

    if not state.get("has_workstreams") or state.get("raci_errors", 0) > 0:
        return {"primary": _rec(
            "Fix ownership (RACI)",
            "Some areas have no single owner, or ownership is split — the #1 source "
            "of free-riders and blame.",
            "EOS Accountability Chart: exactly one Accountable owner per function. "
            "Resolve the errors on the RACI page.",
            "error"), "also": also, "maturity": "Forming"}

    if state.get("decisions_count", 0) == 0:
        return {"primary": _rec(
            "Start a weekly issues + decisions rhythm",
            "Decisions aren't being recorded, so 'we never agreed to that' arguments "
            "and quiet revisionism are inevitable.",
            "EOS Level 10 meeting + IDS (Identify, Discuss, Solve): each week, work "
            "a short issues list to closure and log what you decided.",
            "warn"), "also": also, "maturity": "Operating"}

    # ── Stage 1b: EOS operating rhythm ─────────────────────────────────────────
    if not state.get("has_rocks"):
        also.append("Add 3–7 quarterly Rocks so priorities are binary and owned.")
    if not state.get("has_scorecard"):
        also.append("Set up 5–15 scorecard numbers so the team sees reality weekly.")

    if not state.get("has_issues_resolved"):
        return {"primary": _rec(
            "Run your first Level 10 meeting",
            "You have structure and decisions on record, but no weekly issue-resolution "
            "rhythm yet. Without it, problems pile up instead of getting solved.",
            "The Level 10 page has a 60-minute agenda. The core is IDS: raise an issue, "
            "discuss it with a timer, solve it with a decision + owner. Do this every "
            "week, same day and time. Add Rocks and a Scorecard when ready.",
            "warn"), "also": also, "maturity": "Operating"}

    # ── Stage 2: foundations exist — now measure and coach on health ──────────
    if not pulse:                      # None = below MIN_RESPONSES
        return {"primary": _rec(
            "Run an anonymous pulse",
            f"You have the structure in place but no honest read on how the team "
            f"feels. Collect at least {MIN_RESPONSES} responses to unlock the signal.",
            "Share the Health Pulse with the team. It's anonymous by design — "
            "results stay hidden until enough people respond.",
            "warn"), "also": also, "maturity": "Operating"}

    dim = pulse["per_dimension"]

    # Flag every below-neutral dimension as a secondary note (don't overwhelm).
    for qid, avg in sorted(dim.items(), key=lambda kv: kv[1]):
        if avg < LOW:
            also.append(f"{DIMENSION_OF[qid]} is low ({avg}/5)")

    # The hard one first: chronic low openness means the bottleneck is leadership
    # willingness, which no process fixes. Name it honestly and protect the team.
    if dim.get("openness", 5) < SERIOUS:
        return {"primary": _rec(
            "The bottleneck looks like leadership openness — not process",
            f"'When I give feedback, something changes' scored {dim['openness']}/5. "
            "Adding more process won't help if feedback goes nowhere; it may make "
            "things worse by looking like surveillance.",
            "For the leader: pick the lowest-scoring dimension and make ONE visible "
            "change the team asked for, then say so. For members: the decision log "
            "and anonymous pulse are yours — they keep an honest record regardless. "
            "If nothing changes over repeated cycles, that's information about the "
            "team, not a tooling problem.",
            "error"), "also": also, "maturity": "At risk"}

    # Otherwise coach the single lowest below-neutral dimension.
    low = [(qid, avg) for qid, avg in dim.items() if avg < LOW]
    if low:
        qid, avg = min(low, key=lambda kv: kv[1])
        practice = {
            "safety": "Leader goes first: openly own a mistake at the next meeting, "
                      "and thank people who raise problems. Safety is modeled, not declared.",
            "role_clarity": "Revisit the RACI together; make sure every member can "
                            "name what they're Accountable for.",
            "decisions": "Adopt the EOS Level 10 + IDS weekly rhythm so issues get "
                         "resolved instead of looping.",
            "workload": "Check the RACI load view — rebalance anyone Accountable for "
                        "too much, and involve anyone with no role.",
            "direction": "Adopt an EOS-style Scorecard (5–15 numbers everyone sees) "
                         "plus 3–7 quarterly Rocks so priorities are unmistakable.",
            "communication": "Write a short communication charter: which channel for "
                             "what, and expected response times. Default to async.",
            "credit": "Make credit explicit in the retro — each person presents the "
                      "part they led; record it in the decision log.",
        }.get(qid, "Discuss this dimension openly at the next check-in.")
        return {"primary": _rec(
            f"Improve {DIMENSION_OF[qid].lower()}",
            f"It's your lowest-scoring dimension ({avg}/5).",
            practice, "warn"), "also": [a for a in also if not a.startswith(DIMENSION_OF[qid])],
            "maturity": "Operating"}

    # ── EOS rhythm nudges (secondary, when pulse is healthy) ────────────────
    off_track_rocks = state.get("off_track_rocks", 0)
    if off_track_rocks:
        also.append(f"{off_track_rocks} Rock(s) off track — IDS them at the Level 10")
    if not state.get("has_rocks"):
        also.append("No Rocks set — add 3–7 quarterly priorities")
    if not state.get("has_scorecard"):
        also.append("No Scorecard — add 5–15 weekly numbers the team watches")

    # Everything healthy.
    return {"primary": _rec(
        "Healthy — keep the cadence",
        f"All dimensions are at or above neutral (overall {pulse['overall']}/5).",
        "Maintain the weekly Level 10 rhythm and re-pulse each cycle.",
        "ok"), "also": also, "maturity": "Healthy"}

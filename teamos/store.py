"""Session state + persistence for Team OS.

v1 uses a local JSON file — zero deps, survives restarts. The public API
(init_state / save) hides the backend so pages never touch storage details;
swapping in Google Sheets or SQLite later means implementing them here only.
This mirrors the proven pattern from the TeamUp app.
"""

from __future__ import annotations

import json
from pathlib import Path

from teamos.models import (
    Charter, Decision, Issue, Member, PulseResponse, Rock, ScorecardMetric,
    Workstream, decision_from_dict, issue_from_dict, member_from_dict,
    pulse_from_dict, rock_from_dict, scorecard_from_dict, workstream_from_dict,
)

_FILE = Path("teamos_state.json")


# ── JSON backend ──────────────────────────────────────────────────────────────

def _load() -> dict | None:
    if not _FILE.exists():
        return None
    try:
        return json.loads(_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _serialize(st) -> dict:
    ss = st.session_state
    return {
        "team_name": ss.get("team_name", ""),
        "charter": ss.charter.__dict__.copy(),
        "members": [m.__dict__.copy() for m in ss.members],
        "workstreams": [w.__dict__.copy() for w in ss.workstreams],
        "raci": ss.raci,
        "decisions": [d.__dict__.copy() for d in ss.decisions],
        "pulses": [p.__dict__.copy() for p in ss.pulses],
        "issues": [i.__dict__.copy() for i in ss.issues],
        "rocks": [r.__dict__.copy() for r in ss.rocks],
        "scorecard": [s.__dict__.copy() for s in ss.scorecard],
    }


# ── public API ────────────────────────────────────────────────────────────────

def save(st) -> None:
    """Persist the whole team state to the active backend."""
    _FILE.write_text(json.dumps(_serialize(st), indent=2), encoding="utf-8")


def init_state(st) -> None:
    """Load persisted state into session_state on first run of each session."""
    ss = st.session_state
    if ss.get("_inited"):
        return

    saved = _load() or {}
    ss.team_name = saved.get("team_name", "")
    ss.charter = Charter(**saved["charter"]) if saved.get("charter") else Charter()
    ss.members = [member_from_dict(d) for d in saved.get("members", [])]
    ss.workstreams = [workstream_from_dict(d) for d in saved.get("workstreams", [])]
    # raci: { workstream_id: { member_id: code } }
    ss.raci = saved.get("raci", {})
    ss.decisions = [decision_from_dict(d) for d in saved.get("decisions", [])]
    ss.pulses = [pulse_from_dict(d) for d in saved.get("pulses", [])]
    ss.issues = [issue_from_dict(d) for d in saved.get("issues", [])]
    ss.rocks = [rock_from_dict(d) for d in saved.get("rocks", [])]
    ss.scorecard = [scorecard_from_dict(d) for d in saved.get("scorecard", [])]

    ss._inited = True


# ── demo data (opt-in only) ───────────────────────────────────────────────────

def load_demo(st) -> None:
    """A small, deliberately *flawed* team so the RACI checks have something to
    flag. Never loaded automatically."""
    ss = st.session_state
    ss.team_name = "Robotics Club — Demo"
    ss.charter = Charter(
        mission="Win the regional and bring three new members up to speed.",
        values=["Show up", "Ask early", "Credit the work, not the loudest voice"],
    )
    members = [Member.create(n) for n in ["Avery", "Ben", "Chen", "Dee"]]
    ss.members = members
    ws = [Workstream.create(n) for n in ["Hardware", "Software", "Outreach", "Logistics"]]
    ss.workstreams = ws
    a, b, c, d = (m.id for m in members)
    h, s, o, l = (w.id for w in ws)
    ss.raci = {
        h: {a: "A", b: "R"},
        s: {a: "A", c: "R"},                 # Avery overloaded? only 2 A's here
        o: {a: "A", b: "C"},                 # no Responsible on Outreach
        l: {b: "A", c: "A"},                 # two Accountable on Logistics
        # Dee has no assignment anywhere → free-rider warning
    }
    ss.decisions = [
        Decision.create("Use last year's chassis to save build time", "Avery",
                        "Considered a redesign but we lack time before regionals."),
    ]
    # A few anonymous responses (≥ MIN_RESPONSES) so the pulse + coach light up.
    # Skewed low on openness/credit to show the "leadership openness" detector.
    ss.pulses = [
        PulseResponse.create({"safety": 3, "role_clarity": 2, "decisions": 2,
                              "workload": 2, "direction": 3, "communication": 3,
                              "credit": 2, "openness": 2}),
        PulseResponse.create({"safety": 2, "role_clarity": 3, "decisions": 2,
                              "workload": 2, "direction": 2, "communication": 3,
                              "credit": 2, "openness": 1}),
        PulseResponse.create({"safety": 3, "role_clarity": 2, "decisions": 3,
                              "workload": 3, "direction": 3, "communication": 4,
                              "credit": 3, "openness": 2}),
    ]
    # EOS: Issues, Rocks, Scorecard — show a mix of resolved/open/off-track.
    ss.issues = [
        Issue.create("Parts supplier delayed — need backup", "Ben"),
        Issue.create("No one is updating the outreach social media", "Chen"),
    ]
    ss.issues[0].status = "resolved"
    ss.issues[0].resolution = "Ordered from secondary supplier; 3-day lead time."
    ss.issues[0].owner = "Ben"
    ss.rocks = [
        Rock.create("Qualify for regionals", "Avery", "2026-Q3"),
        Rock.create("Recruit 3 new members", "Dee", "2026-Q3"),
        Rock.create("Redesign outreach materials", "Chen", "2026-Q3"),
    ]
    ss.rocks[1].status = "off_track"
    ss.rocks[1].notes = "Only 1 recruit so far."
    ss.scorecard = [
        ScorecardMetric.create("Build hours / week", "Avery", "> 15", "hrs"),
        ScorecardMetric.create("Outreach posts / week", "Chen", ">= 3", "posts"),
        ScorecardMetric.create("Open issues count", "Ben", "< 5", ""),
    ]
    ss.scorecard[0].entries = {"2026-W24": "18", "2026-W25": "12"}
    ss.scorecard[1].entries = {"2026-W24": "1", "2026-W25": "0"}
    save(st)

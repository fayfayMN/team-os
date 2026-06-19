"""Entities for Team OS.

Kept as plain dataclasses so persistence is a trivial dict round-trip (see
store.py) and future migrations are cheap. Every record carries a
``schema_version`` so we can evolve the shape without breaking saved data —
this is the "more information in later" hook from the plan.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List

SCHEMA_VERSION = 1

# RACI role codes. Exactly one Accountable per workstream; one or more Responsible.
RACI_CODES = {
    "A": "Accountable — owns the outcome (exactly one)",
    "R": "Responsible — does the work",
    "C": "Consulted — gives input before it's done",
    "I": "Informed — told after it's done",
    "": "Not involved",
}


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


@dataclass
class Member:
    id: str
    name: str
    role: str = ""              # free-text, e.g. "Engineer", "President", "Owner"

    @staticmethod
    def create(name: str, role: str = "") -> "Member":
        return Member(id=_new_id("m"), name=name.strip(), role=role.strip())


@dataclass
class Workstream:
    id: str
    name: str
    description: str = ""

    @staticmethod
    def create(name: str, description: str = "") -> "Workstream":
        return Workstream(id=_new_id("w"), name=name.strip(), description=description.strip())


@dataclass
class Decision:
    """Append-only. We never edit history; a reversal is a *new* decision that
    supersedes an old one (set ``supersedes``). This mirrors TeamUp/Clearwork's
    immutable-record stance and is what makes the log trustworthy."""
    id: str
    title: str
    decided_by: str            # member name (free-text so it survives member deletes)
    made_on: str               # ISO date
    context: str = ""          # the "why", and options considered
    supersedes: str = ""       # id of a decision this one replaces

    @staticmethod
    def create(title: str, decided_by: str, context: str = "",
               made_on: str | None = None, supersedes: str = "") -> "Decision":
        return Decision(
            id=_new_id("d"),
            title=title.strip(),
            decided_by=decided_by.strip(),
            made_on=made_on or date.today().isoformat(),
            context=context.strip(),
            supersedes=supersedes,
        )


@dataclass
class PulseResponse:
    """One anonymous health-check submission.

    Deliberately carries **no author field** — there is nothing here to tie a
    response back to a person. Anonymity is structural, not a promise: see
    health.MIN_RESPONSES, which suppresses all results until enough responses
    exist that no single one can be singled out. This is what protects team
    members from an unwilling leader."""
    id: str
    submitted_on: str          # ISO date
    scores: Dict[str, int]     # question_id -> 1..5

    @staticmethod
    def create(scores: Dict[str, int], submitted_on: str | None = None) -> "PulseResponse":
        return PulseResponse(
            id=_new_id("p"),
            submitted_on=submitted_on or date.today().isoformat(),
            scores=dict(scores),
        )


@dataclass
class Issue:
    """EOS IDS (Identify, Discuss, Solve) issue.

    Issues live on the Issues List until they're resolved. Resolution means a
    Decision (logged in the Decision Log) and optionally a to-do assigned to an
    owner. Unresolved issues carry forward to the next Level 10."""
    id: str
    title: str
    raised_by: str             # member name
    raised_on: str             # ISO date
    status: str = "open"       # open | resolved | dropped
    resolved_on: str = ""
    resolution: str = ""       # free-text — what was decided
    owner: str = ""            # who owns the resulting to-do

    @staticmethod
    def create(title: str, raised_by: str, raised_on: str | None = None) -> "Issue":
        return Issue(
            id=_new_id("i"), title=title.strip(), raised_by=raised_by.strip(),
            raised_on=raised_on or date.today().isoformat(),
        )


@dataclass
class Rock:
    """EOS quarterly Rock — one of 3–7 priorities for the quarter.

    A Rock is either done or not done; there's no percentage. It has a single
    owner (accountability) and a target date (the end of the quarter)."""
    id: str
    title: str
    owner: str                 # member name
    quarter: str               # e.g. "2026-Q3"
    status: str = "on_track"   # on_track | off_track | done | dropped
    notes: str = ""

    @staticmethod
    def create(title: str, owner: str, quarter: str) -> "Rock":
        return Rock(id=_new_id("r"), title=title.strip(), owner=owner.strip(),
                    quarter=quarter.strip())


@dataclass
class ScorecardMetric:
    """EOS Scorecard — one of 5–15 weekly numbers the team watches.

    Each metric has a goal (target) and an owner who reports it. Entries are the
    week-by-week actuals, stored as {iso_week: value}."""
    id: str
    name: str
    owner: str                 # member name
    goal: str                  # target, free-text (allows "$10k", "< 3", "95%")
    unit: str = ""             # optional label, e.g. "%", "hours", "$"
    entries: Dict[str, str] = field(default_factory=dict)  # {"2026-W25": "12"}

    @staticmethod
    def create(name: str, owner: str, goal: str, unit: str = "") -> "ScorecardMetric":
        return ScorecardMetric(id=_new_id("sc"), name=name.strip(),
                               owner=owner.strip(), goal=goal.strip(),
                               unit=unit.strip())


@dataclass
class Charter:
    """The living team charter — grows out of TeamUp's Kickoff working agreement."""
    mission: str = ""
    values: List[str] = field(default_factory=list)
    decision_rule: str = (
        "The Accountable owner decides after 10 minutes of disagreement, and we move on."
    )
    checkin_cadence: str = "Weekly sync, plus a retro at every milestone."
    quiet_rule: str = (
        "We ask what's blocking someone directly — coasting is often being lost. "
        "We don't silently do their work; we raise it early at the next check-in."
    )
    credit_rule: str = "Each person owns and presents the part they led."

    def to_markdown(self, team_name: str = "our team") -> str:
        lines = [f"# Charter — {team_name}", ""]
        if self.mission:
            lines += ["## Mission", self.mission, ""]
        if self.values:
            lines += ["## Values", *[f"- {v}" for v in self.values], ""]
        lines += [
            "## How we decide", self.decision_rule, "",
            "## Check-ins", self.checkin_cadence, "",
            "## If someone goes quiet", self.quiet_rule, "",
            "## Credit", self.credit_rule, "",
            "_Agreed by all members. Revisit at each retro._",
        ]
        return "\n".join(lines)


# ── Typed serialization helpers (dataclass <-> dict) ──────────────────────────

def member_from_dict(d: Dict) -> Member:
    return Member(id=d["id"], name=d["name"], role=d.get("role", ""))


def workstream_from_dict(d: Dict) -> Workstream:
    return Workstream(id=d["id"], name=d["name"], description=d.get("description", ""))


def decision_from_dict(d: Dict) -> Decision:
    return Decision(
        id=d["id"], title=d["title"], decided_by=d["decided_by"],
        made_on=d["made_on"], context=d.get("context", ""),
        supersedes=d.get("supersedes", ""),
    )


def pulse_from_dict(d: Dict) -> PulseResponse:
    return PulseResponse(id=d["id"], submitted_on=d["submitted_on"],
                         scores={k: int(v) for k, v in d.get("scores", {}).items()})


def issue_from_dict(d: Dict) -> Issue:
    return Issue(id=d["id"], title=d["title"], raised_by=d["raised_by"],
                 raised_on=d["raised_on"], status=d.get("status", "open"),
                 resolved_on=d.get("resolved_on", ""),
                 resolution=d.get("resolution", ""), owner=d.get("owner", ""))


def rock_from_dict(d: Dict) -> Rock:
    return Rock(id=d["id"], title=d["title"], owner=d["owner"],
                quarter=d["quarter"], status=d.get("status", "on_track"),
                notes=d.get("notes", ""))


def scorecard_from_dict(d: Dict) -> ScorecardMetric:
    return ScorecardMetric(id=d["id"], name=d["name"], owner=d["owner"],
                           goal=d["goal"], unit=d.get("unit", ""),
                           entries=d.get("entries", {}))

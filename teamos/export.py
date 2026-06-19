"""Export engine — generates ready-to-use outputs for external tools.

Three output formats, matched to where small teams actually work:
  - CSV      → Google Sheets / Excel / any spreadsheet
  - Markdown → Notion / Google Docs / any wiki
  - Message  → Slack / Discord / Microsoft Teams (plain-text with formatting)

Each function takes session_state data and returns a string. The page handles
download buttons and copy-to-clipboard. No API keys — the user pastes or
imports. This is the "universal bridge" approach: Team OS stays the source of
truth for structure and health; external tools are the display layer.
"""

from __future__ import annotations

import csv
import io
from typing import Dict, List

from teamos import health
from teamos import raci as raci_check


# ── CSV generators (Google Sheets / Excel) ────────────────────────────────────

def _to_csv(rows: List[List[str]]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerows(rows)
    return buf.getvalue()


def raci_csv(workstreams, members, raci: Dict) -> str:
    header = ["Workstream"] + [m.name for m in members]
    rows = [header]
    for w in workstreams:
        row = [w.name]
        for m in members:
            row.append(raci.get(w.id, {}).get(m.id, ""))
        rows.append(row)
    return _to_csv(rows)


def decisions_csv(decisions) -> str:
    header = ["Date", "Decision", "Decided by", "Context", "Supersedes"]
    rows = [header]
    for d in decisions:
        rows.append([d.made_on, d.title, d.decided_by, d.context, d.supersedes])
    return _to_csv(rows)


def rocks_csv(rocks) -> str:
    header = ["Rock", "Owner", "Quarter", "Status", "Notes"]
    rows = [header]
    for r in rocks:
        rows.append([r.title, r.owner, r.quarter, r.status, r.notes])
    return _to_csv(rows)


def scorecard_csv(metrics) -> str:
    all_weeks = sorted({w for m in metrics for w in m.entries})
    header = ["Metric", "Owner", "Goal", "Unit"] + all_weeks
    rows = [header]
    for m in metrics:
        row = [m.name, m.owner, m.goal, m.unit]
        row += [m.entries.get(w, "") for w in all_weeks]
        rows.append(row)
    return _to_csv(rows)


def issues_csv(issues) -> str:
    header = ["Issue", "Raised by", "Raised on", "Status", "Resolved on",
              "Resolution", "Owner"]
    rows = [header]
    for i in issues:
        rows.append([i.title, i.raised_by, i.raised_on, i.status,
                     i.resolved_on, i.resolution, i.owner])
    return _to_csv(rows)


# ── Markdown generators (Notion / Google Docs / wiki) ─────────────────────────

def charter_md(charter, team_name: str) -> str:
    return charter.to_markdown(team_name)


def raci_md(workstreams, members, raci: Dict) -> str:
    if not workstreams or not members:
        return "_No RACI data yet._"
    lines = ["# RACI Matrix", ""]
    header = "| Workstream | " + " | ".join(m.name for m in members) + " |"
    sep = "|---|" + "|".join("---" for _ in members) + "|"
    lines += [header, sep]
    for w in workstreams:
        cells = [raci.get(w.id, {}).get(m.id, "—") or "—" for m in members]
        lines.append(f"| {w.name} | " + " | ".join(cells) + " |")

    result = raci_check.check(raci, workstreams, members)
    if result["findings"]:
        lines += ["", "## Health check", ""]
        for f in result["findings"]:
            icon = {"error": "🔴", "warn": "🟡", "ok": "🟢"}[f["level"]]
            lines.append(f"- {icon} {f['msg']}")
    return "\n".join(lines)


def decisions_md(decisions, team_name: str) -> str:
    if not decisions:
        return "_No decisions logged yet._"
    superseded = {d.supersedes for d in decisions if d.supersedes}
    lines = [f"# Decision Log — {team_name}", ""]
    for d in reversed(decisions):
        flag = " ~~(superseded)~~" if d.id in superseded else ""
        lines += [f"## {d.title}{flag}", f"_{d.made_on} · {d.decided_by}_", ""]
        if d.context:
            lines += [d.context, ""]
    return "\n".join(lines)


def rocks_md(rocks, team_name: str) -> str:
    if not rocks:
        return "_No Rocks set yet._"
    icon = {"on_track": "🟢", "off_track": "🟡", "done": "✅", "dropped": "⬜"}
    lines = [f"# Quarterly Rocks — {team_name}", ""]
    lines += ["| Rock | Owner | Quarter | Status | Notes |",
              "|---|---|---|---|---|"]
    for r in rocks:
        lines.append(f"| {r.title} | {r.owner} | {r.quarter} | "
                     f"{icon.get(r.status, '')} {r.status} | {r.notes} |")
    return "\n".join(lines)


def scorecard_md(metrics, team_name: str) -> str:
    if not metrics:
        return "_No Scorecard metrics yet._"
    all_weeks = sorted({w for m in metrics for w in m.entries})[-6:]
    lines = [f"# Scorecard — {team_name}", ""]
    header = "| Metric | Owner | Goal | " + " | ".join(all_weeks) + " |"
    sep = "|---|---|---|" + "|".join("---" for _ in all_weeks) + "|"
    lines += [header, sep]
    for m in metrics:
        vals = " | ".join(m.entries.get(w, "—") for w in all_weeks)
        lines.append(f"| {m.name} | {m.owner} | {m.goal} | {vals} |")
    return "\n".join(lines)


# ── Message generators (Slack / Discord / Teams) ─────────────────────────────

def level10_summary_msg(team_name: str, issues, rocks, scorecard,
                        coach_rec: Dict) -> str:
    """A post-meeting summary to paste into the team channel."""
    lines = [f"**Level 10 Summary — {team_name}**", ""]

    open_issues = [i for i in issues if i.status == "open"]
    resolved_today = [i for i in issues if i.status == "resolved"]
    if resolved_today:
        lines.append("**Solved this week:**")
        for i in resolved_today:
            lines.append(f"  ✅ {i.title} → {i.resolution} (owner: {i.owner})")
        lines.append("")
    if open_issues:
        lines.append(f"**Open issues ({len(open_issues)}):**")
        for i in open_issues:
            lines.append(f"  🔸 {i.title} (raised by {i.raised_by})")
        lines.append("")

    off_track = [r for r in rocks if r.status == "off_track"]
    if off_track:
        lines.append("**Rocks off track:**")
        for r in off_track:
            lines.append(f"  🟡 {r.title} — {r.owner}"
                         + (f" ({r.notes})" if r.notes else ""))
        lines.append("")

    off_score = [m for m in scorecard
                 if m.entries and not m.entries.get(sorted(m.entries)[-1], "")]
    if off_score:
        lines.append("**Scorecard gaps (no entry this week):**")
        for m in off_score:
            lines.append(f"  📊 {m.name} — {m.owner}")
        lines.append("")

    if coach_rec:
        p = coach_rec.get("primary", {})
        lines.append(f"**Coach:** {p.get('title', '')}")
        lines.append(f"  → {p.get('practice', '')}")

    return "\n".join(lines)


def pulse_reminder_msg(team_name: str, response_count: int) -> str:
    """A reminder to post in the team channel asking people to take the pulse."""
    needed = health.MIN_RESPONSES - response_count
    if needed > 0:
        return (f"**{team_name} — Health Pulse reminder**\n\n"
                f"🔒 {response_count} response(s) so far — need {needed} more "
                f"before results unlock.\n\n"
                f"It's anonymous. Takes 2 minutes. Your honest read matters.")
    return (f"**{team_name} — Health Pulse reminder**\n\n"
            f"We have {response_count} responses. More voices = better signal.\n\n"
            f"It's anonymous. Takes 2 minutes.")


def full_snapshot_msg(team_name: str, members, workstreams, raci_dict,
                      decisions, issues, rocks, scorecard, charter,
                      coach_rec: Dict) -> str:
    """A comprehensive team snapshot for onboarding or a weekly post."""
    lines = [f"**Team Snapshot — {team_name}**", ""]

    if charter.mission:
        lines += [f"**Mission:** {charter.mission}", ""]

    lines.append(f"**Team ({len(members)}):** "
                 + ", ".join(m.name + (f" ({m.role})" if m.role else "")
                            for m in members))
    lines.append(f"**Workstreams ({len(workstreams)}):** "
                 + ", ".join(w.name for w in workstreams))
    lines.append("")

    open_issues = sum(1 for i in issues if i.status == "open")
    lines.append(f"📋 {len(decisions)} decisions logged · "
                 f"{open_issues} open issues")

    active_rocks = [r for r in rocks if r.status not in ("done", "dropped")]
    off_rocks = sum(1 for r in rocks if r.status == "off_track")
    done_rocks = sum(1 for r in rocks if r.status == "done")
    lines.append(f"🪨 {len(active_rocks)} active Rocks · "
                 f"{done_rocks} done · {off_rocks} off track")
    lines.append(f"📊 {len(scorecard)} scorecard metrics")
    lines.append("")

    if coach_rec:
        p = coach_rec.get("primary", {})
        lines.append(f"**Coach says:** {p.get('title', '')}")

    return "\n".join(lines)

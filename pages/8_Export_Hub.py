"""Export Hub — push Team OS data to wherever your team already works.

Team OS stays the source of truth for structure and health. External tools
(Notion, Google Sheets, Slack, Discord, Teams) are the display layer. This page
generates ready-to-use exports — no API keys needed. Copy, paste, done.
"""

import streamlit as st

from teamos.gate import require_access
from teamos import export, health
from teamos import raci as raci_check
from teamos.store import init_state

st.set_page_config(page_title="Export Hub · Team OS", page_icon="📤", layout="wide")
init_state(st)
require_access()

st.title("📤 Export Hub")
st.caption("Take your team's structure wherever it needs to go — Google Sheets, "
           "Notion, Slack, Discord, Teams. No API keys. Copy or download.")

team = st.session_state.team_name or "our team"

# ── Build coach state once (shared by message generators) ─────────────────────
ch = st.session_state.charter
raci_result = raci_check.check(st.session_state.raci,
                               st.session_state.workstreams,
                               st.session_state.members)
raci_errors = sum(1 for f in raci_result["findings"] if f["level"] == "error")
issues = st.session_state.issues
rocks = st.session_state.rocks
pulse_agg = health.aggregate(st.session_state.pulses)
coach_state = {
    "has_charter": bool(ch.mission),
    "has_workstreams": bool(st.session_state.workstreams),
    "raci_errors": raci_errors,
    "decisions_count": len(st.session_state.decisions),
    "responses_count": len(st.session_state.pulses),
    "pulse": pulse_agg,
    "has_issues_resolved": any(i.status == "resolved" for i in issues),
    "has_rocks": bool(rocks),
    "has_scorecard": bool(st.session_state.scorecard),
    "off_track_rocks": sum(1 for r in rocks if r.status == "off_track"),
}
coach_rec = health.coach(coach_state)

# ── Tabs by target ────────────────────────────────────────────────────────────
tab_sheets, tab_notion, tab_chat = st.tabs([
    "📊 Google Sheets / Excel",
    "📝 Notion / Docs / Wiki",
    "💬 Slack / Discord / Teams",
])

# ═══════════════════════════════════════════════════════════════════════════════
# Google Sheets / Excel (CSV)
# ═══════════════════════════════════════════════════════════════════════════════
with tab_sheets:
    st.markdown("#### CSV exports — import into any spreadsheet")
    st.caption("Google Sheets: File → Import → Upload. Excel: just open the .csv.")

    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.workstreams and st.session_state.members:
            st.download_button("RACI Matrix", export.raci_csv(
                st.session_state.workstreams, st.session_state.members,
                st.session_state.raci), file_name="raci.csv", mime="text/csv")

        if st.session_state.decisions:
            st.download_button("Decision Log", export.decisions_csv(
                st.session_state.decisions), file_name="decisions.csv",
                mime="text/csv")

        if issues:
            st.download_button("Issues List", export.issues_csv(issues),
                               file_name="issues.csv", mime="text/csv")

    with col2:
        if rocks:
            st.download_button("Rocks", export.rocks_csv(rocks),
                               file_name="rocks.csv", mime="text/csv")

        if st.session_state.scorecard:
            st.download_button("Scorecard", export.scorecard_csv(
                st.session_state.scorecard), file_name="scorecard.csv",
                mime="text/csv")

    if not any([st.session_state.workstreams, st.session_state.decisions,
                issues, rocks, st.session_state.scorecard]):
        st.info("Nothing to export yet — add data on the other pages first.")

# ═══════════════════════════════════════════════════════════════════════════════
# Notion / Google Docs / Wiki (Markdown)
# ═══════════════════════════════════════════════════════════════════════════════
with tab_notion:
    st.markdown("#### Markdown exports — paste into Notion, Google Docs, or any wiki")
    st.caption("Notion: paste markdown directly — it converts automatically. "
               "Google Docs: use an add-on like 'Docs to Markdown' or paste as plain text.")

    what = st.selectbox("What to export", [
        "Charter",
        "RACI Matrix + Health Check",
        "Decision Log",
        "Rocks",
        "Scorecard",
        "Everything (full snapshot)",
    ])

    if what == "Charter":
        md = export.charter_md(ch, team)
    elif what == "RACI Matrix + Health Check":
        md = export.raci_md(st.session_state.workstreams,
                            st.session_state.members, st.session_state.raci)
    elif what == "Decision Log":
        md = export.decisions_md(st.session_state.decisions, team)
    elif what == "Rocks":
        md = export.rocks_md(rocks, team)
    elif what == "Scorecard":
        md = export.scorecard_md(st.session_state.scorecard, team)
    else:
        parts = [
            export.charter_md(ch, team),
            "",
            export.raci_md(st.session_state.workstreams,
                           st.session_state.members, st.session_state.raci),
            "",
            export.decisions_md(st.session_state.decisions, team),
            "",
            export.rocks_md(rocks, team),
            "",
            export.scorecard_md(st.session_state.scorecard, team),
        ]
        md = "\n\n---\n\n".join(p for p in parts if p.strip())

    st.code(md, language="markdown")
    st.download_button("Download .md", md,
                       file_name=f"{what.lower().replace(' ', '_')}.md")

# ═══════════════════════════════════════════════════════════════════════════════
# Slack / Discord / Teams (formatted messages)
# ═══════════════════════════════════════════════════════════════════════════════
with tab_chat:
    st.markdown("#### Chat messages — copy and paste into your team channel")
    st.caption("Works in Slack, Discord, Microsoft Teams, or any chat that "
               "supports basic **bold** formatting.")

    msg_type = st.selectbox("Message type", [
        "Level 10 summary (post after your weekly meeting)",
        "Pulse reminder (ask the team to respond)",
        "Team snapshot (onboarding or weekly post)",
    ])

    if msg_type.startswith("Level 10"):
        msg = export.level10_summary_msg(team, issues, rocks,
                                         st.session_state.scorecard, coach_rec)
    elif msg_type.startswith("Pulse"):
        msg = export.pulse_reminder_msg(team, len(st.session_state.pulses))
    else:
        msg = export.full_snapshot_msg(
            team, st.session_state.members, st.session_state.workstreams,
            st.session_state.raci, st.session_state.decisions, issues, rocks,
            st.session_state.scorecard, ch, coach_rec)

    st.code(msg, language="text")
    st.caption("Select all → copy → paste into your channel.")

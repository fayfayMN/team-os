"""Team OS — Streamlit app entry (Home).

A lightweight team collaboration system: keep a team healthy while it works
through an explicit charter, clear decision rights (RACI), and an immutable
decision log. The RUN stage that complements TeamUp (FORM) and Clearwork (PROOF).

Run locally:
    pip install -r requirements.txt
    streamlit run app.py
"""

import streamlit as st

from teamos.store import init_state, load_demo, save

st.set_page_config(page_title="Team OS", page_icon="🧭", layout="wide")
init_state(st)

st.title("🧭 Team OS")
st.caption("Run a healthy collaborative team — startup, small business, or club. "
           "Make the four things explicit that quietly break teams: who decides, "
           "who does the work, how you talk, and whether you're actually healthy.")

team_name = st.text_input("Team / org name", value=st.session_state.team_name,
                          placeholder="e.g. Robotics Club, Acme LLC, Startup XYZ")
if team_name != st.session_state.team_name:
    st.session_state.team_name = team_name
    save(st)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Members", len(st.session_state.members))
c2.metric("Workstreams", len(st.session_state.workstreams))
c3.metric("Decisions logged", len(st.session_state.decisions))
open_issues = sum(1 for i in st.session_state.issues if i.status == "open")
c4.metric("Open issues", open_issues)

st.info("Everything is deterministic and explainable — no API key, no cost. "
        "Data persists to `teamos_state.json`.", icon="🔒")

st.divider()
st.markdown(
    "#### How it works\n"
    "1. **Charter** — agree the mission, values, and the rules for how you work\n"
    "2. **RACI** — make decision rights explicit; the app flags broken ownership\n"
    "3. **Decision Log** — an immutable record of what was decided and why\n"
    "4. **Health Pulse** — anonymous check + coach: one EOS practice at a time\n"
    "5. **Level 10** — weekly meeting with IDS issue resolution\n"
    "6. **Rocks** — 3–7 quarterly priorities, binary (done / not done)\n"
    "7. **Scorecard** — 5–15 weekly numbers everyone watches\n"
    "8. **Export Hub** — push to Google Sheets, Notion, Slack, Discord, or Teams\n"
)

st.markdown("#### Where this fits")
st.markdown(
    "- **TeamUp** — *form* a healthy team (matching + kickoff)\n"
    "- **Team OS (this app)** — *run* it healthily while the work happens\n"
    "- **Clearwork** — *prove* who contributed; reputation flows back to the next team\n"
)

st.divider()
bc1, bc2, _ = st.columns([1, 1, 2])
if bc1.button("Load demo team", help="A deliberately flawed team so the RACI checks light up"):
    load_demo(st)
    st.rerun()
if bc2.button("Reset everything", help="Clear all data"):
    for k in ("team_name", "charter", "members", "workstreams", "raci",
              "decisions", "pulses", "issues", "rocks", "scorecard", "_inited"):
        st.session_state.pop(k, None)
    init_state(st)
    save(st)
    st.rerun()

st.divider()
st.caption("© 2026 [Your Name]. All rights reserved. "
           "Team OS is proprietary software — source available for review only. "
           "Commercial use requires written permission.")

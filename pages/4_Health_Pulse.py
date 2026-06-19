"""Health Pulse + Coach — the centerpiece.

Anonymous by design (no author is ever stored, and results stay hidden until
enough people respond that no one can be singled out). The coach reads both the
team's structure and its pulse and recommends ONE next practice — EOS-native,
explainable, one move at a time."""

import streamlit as st

from teamos.gate import require_access
from teamos import health
from teamos import raci as raci_check
from teamos.models import PulseResponse
from teamos.store import init_state, save

st.set_page_config(page_title="Health Pulse · Team OS", page_icon="❤️‍🩹", layout="wide")
init_state(st)
require_access()

st.title("❤️‍🩹 Health Pulse + Coach")
st.caption("An anonymous read on how the team actually feels — then one concrete "
           "next step. Built so honest answers are safe even when leadership isn't "
           "perfect.")

tab_submit, tab_results = st.tabs(["Take the pulse", "Results + Coach"])

# ── Submit (anonymous) ────────────────────────────────────────────────────────
with tab_submit:
    st.markdown("#### Your honest read (1 = strongly disagree, 5 = strongly agree)")
    st.caption("🔒 Anonymous. No name is attached to your answers, and results stay "
               f"hidden until at least {health.MIN_RESPONSES} people respond.")
    with st.form("pulse", clear_on_submit=True):
        scores = {}
        for q in health.QUESTIONS:
            scores[q["id"]] = st.slider(q["text"], 1, 5, 3, key=f"q_{q['id']}")
        if st.form_submit_button("Submit anonymously", type="primary"):
            st.session_state.pulses.append(PulseResponse.create(scores))
            save(st)
            st.success("Recorded anonymously. Thank you.")

# ── Results + Coach ───────────────────────────────────────────────────────────
with tab_results:
    pulses = st.session_state.pulses
    agg = health.aggregate(pulses)

    st.markdown("#### Pulse")
    if agg is None:
        st.info(f"🔒 {len(pulses)} of {health.MIN_RESPONSES} responses needed. "
                "Results are hidden to protect anonymity until the threshold is met.")
    else:
        st.caption(f"Based on {agg['n']} anonymous responses · "
                   f"overall {agg['overall']}/5")
        for q in health.QUESTIONS:
            v = agg["per_dimension"].get(q["id"])
            if v is None:
                continue
            st.write(f"**{q['dimension']}** — {v}/5")
            st.progress(v / 5)

    st.divider()
    st.markdown("#### Coach — your next move")

    ch = st.session_state.charter
    raci_result = raci_check.check(st.session_state.raci,
                                   st.session_state.workstreams,
                                   st.session_state.members)
    raci_errors = sum(1 for f in raci_result["findings"] if f["level"] == "error")

    issues = st.session_state.issues
    rocks = st.session_state.rocks
    state = {
        "has_charter": bool(ch.mission),
        "has_workstreams": bool(st.session_state.workstreams),
        "raci_errors": raci_errors,
        "decisions_count": len(st.session_state.decisions),
        "responses_count": len(pulses),
        "pulse": agg,
        "has_issues_resolved": any(i.status == "resolved" for i in issues),
        "has_rocks": bool(rocks),
        "has_scorecard": bool(st.session_state.scorecard),
        "off_track_rocks": sum(1 for r in rocks if r.status == "off_track"),
    }
    rec = health.coach(state)
    primary = rec["primary"]

    st.caption(f"Stage: **{rec['maturity']}**")
    box = {"error": st.error, "warn": st.warning, "ok": st.success}[primary["severity"]]
    box(f"**{primary['title']}**\n\n*Why:* {primary['why']}\n\n*Do this:* {primary['practice']}")

    if rec["also"]:
        st.caption("Also worth watching: " + " · ".join(rec["also"]))

    st.caption("The coach surfaces one move at a time on purpose — fix the "
               "foundation before measuring feelings, and never more than one new "
               "habit per cycle.")

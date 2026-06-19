"""Scorecard — EOS weekly numbers.

5–15 measurables, each with an owner and a goal. Enter actuals each week.
The pattern is simple: is each number on or off track? Off-track numbers
become issues for the Level 10's IDS discussion.
"""

from datetime import date

import streamlit as st

from teamos.models import ScorecardMetric
from teamos.store import init_state, save

st.set_page_config(page_title="Scorecard · Team OS", page_icon="📊", layout="wide")
init_state(st)

st.title("📊 Scorecard")
st.caption("5–15 weekly numbers everyone sees. Each has an owner and a goal. "
           "Off-track numbers go to the Issues List at the Level 10.")

metrics = st.session_state.scorecard
names = [m.name for m in st.session_state.members] or ["(add members first)"]

# ── Current ISO week ──────────────────────────────────────────────────────────
today = date.today()
iso_year, iso_week, _ = today.isocalendar()
current_week = f"{iso_year}-W{iso_week:02d}"

# ── Add a metric ──────────────────────────────────────────────────────────────
with st.form("add_metric", clear_on_submit=True):
    cols = st.columns([3, 2, 2, 1, 1])
    m_name = cols[0].text_input("Metric", placeholder="e.g. Revenue")
    m_owner = cols[1].selectbox("Owner", names)
    m_goal = cols[2].text_input("Goal", placeholder="e.g. > 10")
    m_unit = cols[3].text_input("Unit", placeholder="$, %, hrs")
    if cols[4].form_submit_button("Add") and m_name.strip() and m_goal.strip():
        metrics.append(ScorecardMetric.create(m_name, str(m_owner), m_goal, m_unit))
        save(st)
        st.rerun()

if not metrics:
    st.info("No metrics yet. Add 5–15 weekly numbers the team should watch.")
    st.stop()

# ── Guardrail ─────────────────────────────────────────────────────────────────
if len(metrics) > 15:
    st.warning(f"You have {len(metrics)} metrics — EOS recommends 5–15. Too many "
               "numbers means nobody watches any of them.")

st.divider()

# ── This week's entry ─────────────────────────────────────────────────────────
st.markdown(f"#### Week {current_week}")
changed = False
header = st.columns([3, 2, 2, 2, 1])
header[0].markdown("**Metric**")
header[1].markdown("**Owner**")
header[2].markdown("**Goal**")
header[3].markdown(f"**Actual ({current_week})**")
header[4].markdown("**Del**")

for metric in metrics:
    row = st.columns([3, 2, 2, 2, 1])
    row[0].write(f"{metric.name}" + (f" ({metric.unit})" if metric.unit else ""))
    row[1].write(metric.owner)
    row[2].write(metric.goal)
    cur_val = metric.entries.get(current_week, "")
    new_val = row[3].text_input("val", value=cur_val, key=f"sc_{metric.id}",
                                label_visibility="collapsed", placeholder="—")
    if new_val != cur_val:
        metric.entries[current_week] = new_val
        changed = True
    if row[4].button("✕", key=f"del_{metric.id}"):
        st.session_state.scorecard = [s for s in metrics if s.id != metric.id]
        save(st)
        st.rerun()

if changed:
    save(st)

# ── History (last 6 weeks) ────────────────────────────────────────────────────
st.divider()
all_weeks = sorted({w for m in metrics for w in m.entries}, reverse=True)[:6]
if all_weeks:
    st.markdown("#### Recent weeks")
    data = []
    for metric in metrics:
        row_data = {"Metric": metric.name, "Goal": metric.goal}
        for w in all_weeks:
            row_data[w] = metric.entries.get(w, "—")
        data.append(row_data)
    st.dataframe(data, use_container_width=True, hide_index=True)

"""Decision Log — an immutable record of what was decided and why.

Append-only on purpose: you never edit history. Reversing a past call means
logging a *new* decision that supersedes the old one. A trustworthy record is
what stops "we never agreed to that" arguments and quiet revisionism."""

import streamlit as st

from teamos.gate import require_access
from teamos.models import Decision
from teamos.store import init_state, save

st.set_page_config(page_title="Decision Log · Team OS", page_icon="🗳️", layout="wide")
init_state(st)
require_access()

st.title("🗳️ Decision Log")
st.caption("Capture decisions the moment they're made — what, who decided, and why. "
           "Append-only: to reverse a call, log a new one that supersedes it.")

decisions = st.session_state.decisions
names = [m.name for m in st.session_state.members]

# ── Add a decision ────────────────────────────────────────────────────────────
with st.form("add_decision", clear_on_submit=True):
    title = st.text_input("Decision", placeholder="e.g. Ship without the export feature")
    if names:
        decided_by = st.selectbox("Decided by", names)
    else:
        decided_by = st.text_input("Decided by", placeholder="name")
    context = st.text_area("Why / options considered (the reasoning)",
                           placeholder="What problem, what alternatives, why this one.")
    supersedes = st.selectbox(
        "Supersedes an earlier decision? (optional)",
        ["—"] + [f"{d.title} ({d.made_on})" for d in decisions],
    )
    if st.form_submit_button("Log decision", type="primary"):
        if not title.strip() or not str(decided_by).strip():
            st.error("Decision and decider are required.")
        else:
            sup_id = ""
            if supersedes != "—":
                idx = [f"{d.title} ({d.made_on})" for d in decisions].index(supersedes)
                sup_id = decisions[idx].id
            decisions.append(Decision.create(title, str(decided_by), context, supersedes=sup_id))
            save(st)
            st.success("Logged.")
            st.rerun()

st.divider()

# ── The log ───────────────────────────────────────────────────────────────────
if not decisions:
    st.caption("No decisions logged yet.")
    st.stop()

superseded_ids = {d.supersedes for d in decisions if d.supersedes}
by_id = {d.id: d for d in decisions}

for d in reversed(decisions):           # newest first
    active = d.id not in superseded_ids
    title = d.title if active else f"~~{d.title}~~ (superseded)"
    with st.container(border=True):
        st.markdown(f"**{title}**")
        meta = f"{d.made_on} · decided by {d.decided_by}"
        if d.supersedes and d.supersedes in by_id:
            meta += f" · replaces *{by_id[d.supersedes].title}*"
        st.caption(meta)
        if d.context:
            st.write(d.context)

st.divider()
md_lines = [f"# Decision Log — {st.session_state.team_name or 'our team'}", ""]
for d in decisions:
    flag = " (superseded)" if d.id in superseded_ids else ""
    md_lines += [f"## {d.title}{flag}", f"_{d.made_on} · {d.decided_by}_", "", d.context or "", ""]
md = "\n".join(md_lines)
st.download_button("Download decision-log.md", md, file_name="decision-log.md")

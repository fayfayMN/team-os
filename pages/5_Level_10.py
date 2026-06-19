"""Level 10 Meeting — the EOS weekly operating rhythm.

Same time, same agenda, every week. The core of the meeting is the Issues List
worked through IDS (Identify → Discuss → Solve). Resolution means a decision
(→ Decision Log) and an owner. Open issues carry forward automatically.

The 60-minute agenda:
 1. Good news / wins              (5 min)
 2. Scorecard review              (5 min)
 3. Rock review                   (5 min)
 4. Headlines / updates           (5 min)
 5. To-do review                  (5 min)
 6. IDS — work the issues list    (30 min)
 7. Conclude — recap + rate       (5 min)
"""

from datetime import date

import streamlit as st

from teamos.gate import require_access
from teamos.models import Decision, Issue
from teamos.store import init_state, save

st.set_page_config(page_title="Level 10 · Team OS", page_icon="🔟", layout="wide")
init_state(st)
require_access()

st.title("🔟 Level 10 Meeting")
st.caption("The EOS weekly rhythm. Same time, same agenda, every week. The heart "
           "is the **Issues List** — IDS (Identify, Discuss, Solve) until it's "
           "resolved or dropped. Decisions auto-feed the Decision Log.")

issues = st.session_state.issues
names = [m.name for m in st.session_state.members] or ["(add members first)"]

# ── Agenda cheatsheet ─────────────────────────────────────────────────────────
with st.expander("60-minute agenda cheatsheet"):
    st.markdown(
        "| Min | Step | What to do |\n"
        "|-----|------|------------|\n"
        "| 0–5 | **Good news** | Each person shares one personal + one professional win |\n"
        "| 5–10 | **Scorecard** | Review the numbers — on/off track? (→ Scorecard page) |\n"
        "| 10–15 | **Rock review** | Each Rock owner: on/off track? (→ Rocks page) |\n"
        "| 15–20 | **Headlines** | Quick updates — no discussion, just FYI |\n"
        "| 20–25 | **To-do review** | Last week's to-dos — done or not done? |\n"
        "| 25–55 | **IDS** | Work the Issues List below — Identify, Discuss, Solve |\n"
        "| 55–60 | **Conclude** | Recap decisions + to-dos; rate the meeting 1–10 |\n"
    )

st.divider()

# ── Raise a new issue ─────────────────────────────────────────────────────────
st.markdown("#### Issues List (IDS)")
with st.form("raise_issue", clear_on_submit=True):
    cols = st.columns([3, 2, 1])
    i_title = cols[0].text_input("Issue", placeholder="What's the problem or question?")
    i_by = cols[1].selectbox("Raised by", names)
    if cols[2].form_submit_button("Add to list") and i_title.strip():
        issues.append(Issue.create(i_title, str(i_by)))
        save(st)
        st.rerun()

# ── Open issues ───────────────────────────────────────────────────────────────
open_issues = [i for i in issues if i.status == "open"]
resolved_issues = [i for i in issues if i.status != "open"]

if not open_issues:
    st.success("No open issues — clean slate for the week.")
else:
    st.caption(f"{len(open_issues)} open issue(s) to work through:")
    for issue in open_issues:
        with st.container(border=True):
            st.markdown(f"**{issue.title}**")
            st.caption(f"Raised by {issue.raised_by} on {issue.raised_on}")

            with st.expander("Resolve (IDS)"):
                resolution = st.text_area("What was decided?",
                                          key=f"res_{issue.id}",
                                          placeholder="The solution, action, or next step.")
                owner = st.selectbox("Who owns the to-do?", names,
                                     key=f"own_{issue.id}")
                c1, c2 = st.columns(2)
                if c1.button("Solve", key=f"solve_{issue.id}", type="primary"):
                    if resolution.strip():
                        issue.status = "resolved"
                        issue.resolved_on = date.today().isoformat()
                        issue.resolution = resolution.strip()
                        issue.owner = str(owner)
                        st.session_state.decisions.append(
                            Decision.create(
                                f"[IDS] {issue.title}",
                                str(owner),
                                f"Issue raised by {issue.raised_by}. "
                                f"Resolution: {resolution.strip()}",
                            )
                        )
                        save(st)
                        st.rerun()
                    else:
                        st.error("Write what was decided before resolving.")
                if c2.button("Drop", key=f"drop_{issue.id}",
                             help="Not worth solving — remove from the list"):
                    issue.status = "dropped"
                    issue.resolved_on = date.today().isoformat()
                    save(st)
                    st.rerun()

# ── Resolved / dropped ───────────────────────────────────────────────────────
if resolved_issues:
    with st.expander(f"Resolved / dropped ({len(resolved_issues)})"):
        for issue in reversed(resolved_issues):
            label = "Resolved" if issue.status == "resolved" else "Dropped"
            st.markdown(f"**{issue.title}** — {label} {issue.resolved_on}")
            if issue.resolution:
                st.caption(f"→ {issue.resolution} (owner: {issue.owner})")

"""Charter — the living team agreement. Spend the first effort on people and
rules, not just tasks. This is the document you point back to when things drift."""

import streamlit as st

from teamos.models import Member
from teamos.store import init_state, save

st.set_page_config(page_title="Charter · Team OS", page_icon="📜", layout="wide")
init_state(st)

st.title("📜 Team Charter")
st.caption("The shared contract. Agreeing this up front is your defense against "
           "free riders, credit-takers, and silent resentment later.")

ch = st.session_state.charter

# ── Members ───────────────────────────────────────────────────────────────────
st.markdown("#### Members")
with st.form("add_member", clear_on_submit=True):
    cols = st.columns([2, 2, 1])
    m_name = cols[0].text_input("Name")
    m_role = cols[1].text_input("Role (optional)", placeholder="e.g. Engineer, President, Owner")
    if cols[2].form_submit_button("Add member") and m_name.strip():
        st.session_state.members.append(Member.create(m_name, m_role))
        save(st)
        st.rerun()

if st.session_state.members:
    for m in st.session_state.members:
        c1, c2 = st.columns([5, 1])
        c1.write(f"**{m.name}**" + (f" — {m.role}" if m.role else ""))
        if c2.button("Remove", key=f"rm_{m.id}"):
            st.session_state.members = [x for x in st.session_state.members if x.id != m.id]
            # clean any RACI rows that referenced them
            for ws in st.session_state.raci.values():
                ws.pop(m.id, None)
            save(st)
            st.rerun()
else:
    st.caption("No members yet — add the people on this team.")

st.divider()

# ── Charter fields ────────────────────────────────────────────────────────────
with st.form("charter"):
    mission = st.text_area("Mission — what are we here to do?", value=ch.mission,
                           placeholder="One or two sentences everyone would agree to.")
    values_txt = st.text_area("Values (one per line)", value="\n".join(ch.values),
                              placeholder="Show up\nAsk early\nCredit the work, not the loudest voice")
    decision_rule = st.text_area("How we decide when stuck", value=ch.decision_rule)
    checkin_cadence = st.text_area("Check-ins", value=ch.checkin_cadence)
    quiet_rule = st.text_area("If someone goes quiet", value=ch.quiet_rule)
    credit_rule = st.text_area("How credit is handled", value=ch.credit_rule)

    if st.form_submit_button("Save charter", type="primary"):
        ch.mission = mission.strip()
        ch.values = [v.strip() for v in values_txt.splitlines() if v.strip()]
        ch.decision_rule = decision_rule.strip()
        ch.checkin_cadence = checkin_cadence.strip()
        ch.quiet_rule = quiet_rule.strip()
        ch.credit_rule = credit_rule.strip()
        save(st)
        st.success("Charter saved.")

st.divider()
st.markdown("#### Export")
md = ch.to_markdown(st.session_state.team_name or "our team")
st.caption("Paste into your team channel and have everyone react ✅.")
st.code(md, language="markdown")
st.download_button("Download charter.md", md, file_name="charter.md")

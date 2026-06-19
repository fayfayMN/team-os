"""RACI — make decision rights explicit, then let the app check the structure.

R/A/C/I = Responsible (does it) / Accountable (owns it, exactly one) /
Consulted (input before) / Informed (told after)."""

import streamlit as st

from teamos.gate import require_access
from teamos.models import RACI_CODES, Workstream
from teamos import raci as raci_check
from teamos.store import init_state, save

st.set_page_config(page_title="RACI · Team OS", page_icon="🧩", layout="wide")
init_state(st)
require_access()

st.title("🧩 RACI — who decides, who does")
st.caption("Ambiguity about ownership is the #1 driver of free-riders and burnt-out "
           "heroes. Fill the grid, then run the health check.")

members = st.session_state.members
workstreams = st.session_state.workstreams
raci = st.session_state.raci

if not members:
    st.warning("Add members on the **Charter** page first.")
    st.stop()

# ── Manage workstreams ────────────────────────────────────────────────────────
with st.expander("Workstreams (the areas of work this team owns)", expanded=not workstreams):
    with st.form("add_ws", clear_on_submit=True):
        cols = st.columns([2, 3, 1])
        w_name = cols[0].text_input("Workstream")
        w_desc = cols[1].text_input("Description (optional)")
        if cols[2].form_submit_button("Add") and w_name.strip():
            st.session_state.workstreams.append(Workstream.create(w_name, w_desc))
            save(st)
            st.rerun()
    for w in workstreams:
        c1, c2 = st.columns([5, 1])
        c1.write(f"**{w.name}**" + (f" — {w.description}" if w.description else ""))
        if c2.button("Remove", key=f"rmw_{w.id}"):
            st.session_state.workstreams = [x for x in workstreams if x.id != w.id]
            st.session_state.raci.pop(w.id, None)
            save(st)
            st.rerun()

if not workstreams:
    st.info("Add at least one workstream above to build the matrix.")
    st.stop()

# ── The grid ──────────────────────────────────────────────────────────────────
st.markdown("#### Assignment grid")
st.caption(" · ".join(f"**{k or '—'}** = {v}" for k, v in RACI_CODES.items()))

codes = list(RACI_CODES.keys())
changed = False
header = st.columns([2] + [1] * len(members))
header[0].markdown("**Workstream**")
for i, m in enumerate(members):
    header[i + 1].markdown(f"**{m.name}**")

for w in workstreams:
    row = st.columns([2] + [1] * len(members))
    row[0].write(w.name)
    cur = raci.setdefault(w.id, {})
    for i, m in enumerate(members):
        val = row[i + 1].selectbox(
            f"{w.id}_{m.id}", codes,
            index=codes.index(cur.get(m.id, "")),
            label_visibility="collapsed", key=f"sel_{w.id}_{m.id}",
        )
        if val != cur.get(m.id, ""):
            cur[m.id] = val
            changed = True

if changed:
    save(st)

st.divider()

# ── Health check ──────────────────────────────────────────────────────────────
st.markdown("#### Health check")
result = raci_check.check(raci, workstreams, members)
st.progress(result["score"], text=f"Ownership health: {int(result['score'] * 100)}%  ·  {result['summary']}")

for f in result["findings"]:
    if f["level"] == "error":
        st.error(f["msg"])
    elif f["level"] == "warn":
        st.warning(f["msg"])
    else:
        st.success(f["msg"])

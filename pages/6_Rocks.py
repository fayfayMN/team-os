"""Rocks — EOS quarterly priorities.

3–7 things that *must* get done this quarter. Each Rock has one owner and is
binary: done or not done. "Off track" is a flag, not a failure — it triggers
the IDS discussion at the Level 10 so the team can help unblock it.
"""

import streamlit as st

from teamos.models import Rock
from teamos.store import init_state, save

st.set_page_config(page_title="Rocks · Team OS", page_icon="🪨", layout="wide")
init_state(st)

st.title("🪨 Quarterly Rocks")
st.caption("3–7 priorities for the quarter. One owner each, binary (done / not done). "
           "'Off track' isn't a punishment — it's a signal to IDS at the Level 10.")

rocks = st.session_state.rocks
names = [m.name for m in st.session_state.members] or ["(add members first)"]
STATUSES = ["on_track", "off_track", "done", "dropped"]
STATUS_LABEL = {"on_track": "On track", "off_track": "Off track",
                "done": "Done", "dropped": "Dropped"}
STATUS_ICON = {"on_track": "🟢", "off_track": "🟡", "done": "✅", "dropped": "⬜"}

# ── Add a Rock ────────────────────────────────────────────────────────────────
with st.form("add_rock", clear_on_submit=True):
    cols = st.columns([3, 2, 1, 1])
    r_title = cols[0].text_input("Rock", placeholder="e.g. Launch the beta")
    r_owner = cols[1].selectbox("Owner", names)
    r_quarter = cols[2].text_input("Quarter", placeholder="2026-Q3")
    if cols[3].form_submit_button("Add") and r_title.strip() and r_quarter.strip():
        rocks.append(Rock.create(r_title, str(r_owner), r_quarter))
        save(st)
        st.rerun()

if not rocks:
    st.info("No Rocks yet. Add 3–7 quarterly priorities above.")
    st.stop()

# ── Guardrail ─────────────────────────────────────────────────────────────────
active = [r for r in rocks if r.status not in ("done", "dropped")]
if len(active) > 7:
    st.warning(f"You have {len(active)} active Rocks — EOS recommends 3–7. "
               "Too many priorities means nothing is a priority.")
elif len(active) < 3 and active:
    st.info(f"Only {len(active)} active Rock(s). That's fine early on, but a full "
            "quarter typically needs 3–7.")

st.divider()

# ── Rock review ───────────────────────────────────────────────────────────────
changed = False
for rock in rocks:
    icon = STATUS_ICON[rock.status]
    with st.container(border=True):
        c1, c2, c3 = st.columns([4, 2, 2])
        c1.markdown(f"{icon} **{rock.title}**")
        c1.caption(f"Owner: {rock.owner} · {rock.quarter}")
        new_status = c2.selectbox(
            "Status", STATUSES, index=STATUSES.index(rock.status),
            format_func=lambda s: STATUS_LABEL[s], key=f"rs_{rock.id}",
            label_visibility="collapsed",
        )
        if new_status != rock.status:
            rock.status = new_status
            changed = True
        new_notes = c3.text_input("Notes", value=rock.notes,
                                  key=f"rn_{rock.id}", label_visibility="collapsed",
                                  placeholder="quick note")
        if new_notes != rock.notes:
            rock.notes = new_notes
            changed = True

if changed:
    save(st)

# ── Summary ───────────────────────────────────────────────────────────────────
st.divider()
done_pct = sum(1 for r in rocks if r.status == "done") / len(rocks) if rocks else 0
off_ct = sum(1 for r in rocks if r.status == "off_track")
st.progress(done_pct, text=f"{int(done_pct * 100)}% done · "
            f"{off_ct} off track · {len(active)} active")

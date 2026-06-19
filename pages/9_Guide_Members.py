"""Team Member Guide — accessible inside the app."""

from pathlib import Path
import streamlit as st
from teamos.gate import require_access

st.set_page_config(page_title="Member Guide · Team OS", page_icon="📖", layout="wide")
require_access()

st.title("📖 Team Member Guide")
st.caption("What you need to know as a team member using Team OS.")

guide = Path(__file__).resolve().parent.parent / "GUIDE_MEMBER.md"
if guide.exists():
    st.markdown(guide.read_text(encoding="utf-8"))
else:
    st.error("Guide file not found — expected GUIDE_MEMBER.md in the project root.")

"""Owner / Admin Guide — accessible inside the app."""

from pathlib import Path
import streamlit as st
from teamos.gate import require_access

st.set_page_config(page_title="Owner Guide · Team OS", page_icon="📖", layout="wide")
require_access()

st.title("📖 Owner / Admin Guide")
st.caption("How to set up and run Team OS for your team.")

guide = Path(__file__).resolve().parent.parent / "GUIDE_OWNER.md"
if guide.exists():
    st.markdown(guide.read_text(encoding="utf-8"))
else:
    st.error("Guide file not found — expected GUIDE_OWNER.md in the project root.")

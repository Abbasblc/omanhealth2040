"""omanhealth2040: temporary, password-protected live preview of the HEALTH AI
evidence dashboard (Oman Vision 2040 health priority). Built only from public documents.
The dashboard is stored encrypted; the password entered here is the decryption key."""
import base64
from pathlib import Path

import streamlit as st
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

st.set_page_config(page_title="Oman Vision 2040 health evidence (HEALTH AI)", page_icon="🇴🇲",
                   layout="wide", initial_sidebar_state="collapsed")
st.markdown("""<style> header[data-testid="stHeader"], footer, #MainMenu, [data-testid="stToolbar"],
  [data-testid="stDecoration"] {display:none !important;} </style>""", unsafe_allow_html=True)

ENC = Path(__file__).parent / "dashboard.enc"


@st.cache_data(show_spinner=False, max_entries=4)
def decrypt(password: str):
    blob = ENC.read_bytes()
    salt, token = blob[:16], blob[16:]
    key = base64.urlsafe_b64encode(
        PBKDF2HMAC(hashes.SHA256(), 32, salt, 600_000).derive(password.encode()))
    try:
        return Fernet(key).decrypt(token).decode("utf-8")
    except InvalidToken:
        return None


html = st.session_state.get("html")
if html is None:
    _, mid, _ = st.columns([1, 1.2, 1])
    with mid:
        st.markdown("<div style='height:12vh'></div>", unsafe_allow_html=True)
        st.markdown("### Oman Vision 2040 health evidence")
        st.caption("HEALTH AI · Draft for discussion · رؤية عُمان ٢٠٤٠ · أولوية الصحة")
        with st.form("login"):
            pw = st.text_input("Access password · كلمة المرور", type="password")
            ok = st.form_submit_button("Open · فتح", use_container_width=True)
        if ok:
            with st.spinner("Opening…"):
                html = decrypt(pw.strip())
            if html is None:
                st.error("Wrong password · كلمة المرور غير صحيحة")
            else:
                st.session_state["html"] = html
                st.rerun()
    st.stop()

st.markdown("""<style> .block-container {padding:0 !important; max-width:100% !important;}
  [data-testid="stAppViewContainer"] > .main {padding:0 !important;}
  iframe {height: 100vh !important; width: 100% !important; border: 0;} </style>""",
            unsafe_allow_html=True)
if hasattr(st, "iframe"):
    st.iframe(html, height=900)
else:
    import streamlit.components.v1 as components
    components.html(html, height=900, scrolling=True)

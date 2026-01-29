"""Admin Frontend - Member approval and management."""

import html
import os

import streamlit as st

from utils.css import load_css
from utils.totp import verify_totp, get_provisioning_uri, get_current_otp

# Page config
st.set_page_config(
    page_title="Jaram Admin",
    page_icon="⚙️",
    layout="wide",
)

# Load CSS file
load_css()
# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_page" not in st.session_state:
    st.session_state.current_page = "dashboard"

# Login check
if not st.session_state.authenticated:
    st.markdown("""
    <div class="login-container">
        <div class="terminal-login">
            <div class="terminal-header">
                <span class="terminal-title">JARAM_ADMIN_TERMINAL</span>
                <span class="terminal-version">v1.0.0</span>
            </div>
            <div class="terminal-prompt">$ sudo auth --totp</div>
            <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">Enter your 6-digit TOTP code to authenticate</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        otp = st.text_input(
            "TOTP",
            type="password",
            max_chars=6,
            placeholder="••••••",
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("AUTHENTICATE", use_container_width=True, type="primary")

    if submitted:
        if otp and len(otp) == 6 and otp.isdigit():
            if verify_totp(otp):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error(">> AUTHENTICATION FAILED: Invalid TOTP code")
        else:
            st.error(">> ERROR: TOTP must be exactly 6 digits")

    st.markdown("---")

    # Development helper - only show in development mode
    if os.getenv("TOTP_DEBUG", "").lower() in ("1", "true"):
        with st.expander(">> DEBUG_TOOLS"):
            st.warning("⚠️ REMOVE IN PRODUCTION")
            current_otp = get_current_otp()
            st.markdown(f"""
            <div class="terminal-prompt" style="font-size: 0.875rem;">
                CURRENT_TOTP: <span style="color: var(--jaram-red);">{current_otp}</span>
            </div>
            """, unsafe_allow_html=True)

            provisioning_uri = get_provisioning_uri()
            st.text_area("PROVISIONING_URI", value=provisioning_uri, height=100, label_visibility="collapsed")

            from qrcode import QRCode
            qr = QRCode(version=1, box_size=10, border=4)
            qr.add_data(provisioning_uri)
            qr.make(fit=True)

            # Create QR code image
            from io import BytesIO
            img = qr.make_image(fill_color="black", back_color="white")
            buf = BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)

            st.image(buf, caption="Scan with Google Authenticator")

    st.stop()

# Authenticated - Show main app
st.markdown("""
<div class="main-header">
    <h1><span style="color: var(--jaram-red);">▶</span> JARAM_ADMIN_DASHBOARD</h1>
</div>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.markdown("""
    <div style="padding: 1.5rem 0; margin-bottom: 1rem; border-bottom: 1px solid var(--border-primary);">
        <h2 style="font-size: 1rem; letter-spacing: 0.15em; color: var(--jaram-red);">NAVIGATION</h2>
    </div>
    """, unsafe_allow_html=True)
    # Get index safely, default to 0 (dashboard) if current_page is invalid
    page_index_map = {"dashboard": 0, "pending": 1, "members": 2}
    page_index = page_index_map.get(st.session_state.current_page, 0)

    page = st.radio(
        "",
        ["Dashboard", "Pending", "Members"],
        index=page_index,
        key="nav_radio",
        label_visibility="collapsed",
    )

    # Update current page
    page_map = {"Dashboard": "dashboard", "Pending": "pending", "Members": "members"}
    st.session_state.current_page = page_map[page]

    st.markdown("---")

    # API info
    api_base = os.getenv('API_BASE_URL', 'http://localhost:8000')
    st.markdown(f"""
    <div style="font-family: var(--font-mono); font-size: 0.7rem; color: var(--text-muted);">
        API_ENDPOINT: {html.escape(api_base)}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Logout button
    if st.button("LOGOUT", use_container_width=True, type="secondary"):
        st.session_state.authenticated = False
        st.rerun()

# Route to page
if st.session_state.current_page == "dashboard":
    st.switch_page("pages/01_대시보드.py")
elif st.session_state.current_page == "pending":
    st.switch_page("pages/02_승인_대기.py")
elif st.session_state.current_page == "members":
    st.switch_page("pages/03_회원_관리.py")
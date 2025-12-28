"""Admin Frontend - Member approval and management."""

import os
import streamlit as st

from utils.totp import verify_totp, get_provisioning_uri, get_current_otp

# Page config
st.set_page_config(
    page_title="Jaram Admin",
    page_icon="⚙️",
    layout="wide",
)

# Custom CSS
st.markdown("""
<style>
    .login-container {
        max-width: 400px;
        margin: 80px auto;
        padding: 2rem;
        text-align: center;
    }
    .main-header {
        text-align: center;
        padding: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_page" not in st.session_state:
    st.session_state.current_page = "dashboard"

# Login check
if not st.session_state.authenticated:
    st.markdown("""
    <div class="login-container">
        <h1>⚙️ 자람 (Jaram) 관리자</h1>
        <p>TOTP를 입력하여 로그인하세요.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        otp = st.text_input(
            "TOTP (6자리)",
            type="password",
            max_chars=6,
            placeholder="123456",
        )
        submitted = st.form_submit_button("로그인", use_container_width=True, type="primary")

    if submitted:
        if otp and len(otp) == 6 and otp.isdigit():
            if verify_totp(otp):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("TOTP가 올바르지 않습니다.")
        else:
            st.error("6자리 숫자를 입력해주세요.")

    st.markdown("---")

    # Development helper - only show in development mode
    if os.getenv("TOTP_DEBUG", "").lower() in ("1", "true"):
        with st.expander("개발용 도구"):
            st.warning("⚠️ 운영 환경에서는 제거하세요")
            current_otp = get_current_otp()
            st.code(f"현재 TOTP: {current_otp}", language="")

            provisioning_uri = get_provisioning_uri()
            st.text_area("Provisioning URI (QR 코드용)", value=provisioning_uri, height=100)

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

            st.image(buf, caption="Google Authenticator로 스캔")

    st.stop()

# Authenticated - Show main app
st.markdown("""
<div class="main-header">
    <h1>⚙️ 자람 (Jaram) 관리자</h1>
</div>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.title("메뉴")
    # Get index safely, default to 0 (dashboard) if current_page is invalid
    page_index_map = {"dashboard": 0, "pending": 1, "members": 2}
    page_index = page_index_map.get(st.session_state.current_page, 0)

    page = st.radio(
        "Navigation",
        ["대시보드", "승인 대기", "회원 관리"],
        index=page_index,
        key="nav_radio",
    )

    # Update current page
    page_map = {"대시보드": "dashboard", "승인 대기": "pending", "회원 관리": "members"}
    st.session_state.current_page = page_map[page]

    st.markdown("---")

    # API info
    st.caption(f"API: {os.getenv('API_BASE_URL', 'http://localhost:8000')}")

    st.markdown("---")

    # Logout button
    if st.button("로그아웃", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# Route to page
if st.session_state.current_page == "dashboard":
    st.switch_page("pages/01_대시보드.py")
elif st.session_state.current_page == "pending":
    st.switch_page("pages/02_승인_대기.py")
elif st.session_state.current_page == "members":
    st.switch_page("pages/03_회원_관리.py")
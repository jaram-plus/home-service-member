"""Profile update page with magic link authentication."""

import os
import streamlit as st

from utils.api import request_profile_update_link

st.set_page_config(
    page_title="프로필 수정 - Jaram",
    page_icon="✏️",
    layout="centered",
)

st.title("프로필 수정")
st.markdown("---")

# Session state
if "profile_email_sent" not in st.session_state:
    st.session_state.profile_email_sent = False
if "profile_email" not in st.session_state:
    st.session_state.profile_email = None
if "profile_authenticated" not in st.session_state:
    st.session_state.profile_authenticated = False

# Step 1: Request magic link
if not st.session_state.profile_authenticated:
    st.subheader("1. 인증 이메일 받기")

    if st.session_state.profile_email_sent:
        st.markdown(f"""
        <div class="info-box">
            <p><strong>{st.session_state.profile_email}</strong>로 인증 링크를 발송했습니다.</p>
            <p>이메일에 있는 링크를 클릭해주세요.</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("다른 이메일로 다시 받기", use_container_width=True):
            st.session_state.profile_email_sent = False
            st.session_state.profile_email = None
            st.rerun()
    else:
        with st.form("request_magic_link"):
            email = st.text_input(
                "가입한 이메일",
                placeholder="example@email.com",
                max_chars=100,
            )

            submitted = st.form_submit_button("인증 링크 받기", use_container_width=True)

            if submitted:
                if not email or "@" not in email:
                    st.error("올바른 이메일을 입력해주세요.")
                    st.stop()

                try:
                    request_profile_update_link(email.strip().lower())

                    st.session_state.profile_email_sent = True
                    st.session_state.profile_email = email.strip().lower()
                    st.rerun()

                except Exception as e:
                    error_detail = str(e)
                    if "not found" in error_detail.lower():
                        st.error("가입되지 않은 이메일입니다.")
                    else:
                        st.error(f"오류가 발생했습니다: {error_detail}")

    st.markdown("---")
    st.info("💡 인증 링크는 발송 후 30분간 유효합니다.")

    # Note: 실제 인증은 URL 쿼리 파라미터로 토큰을 받아 처리해야 함
    # Streamlit의 URL 파라미터 처리는 별도 구현 필요
    st.markdown("""
    ### 🔐 인증 방법

    이메일로 받은 링크를 클릭하면 프로필 수정 화면이 나타납니다.

    *Note: 현재 개발 중입니다. 실제 배포 시 URL 파라미터 기반 인증이 구현됩니다.*
    """)

else:
    # Step 2: Profile update form (after authentication)
    st.subheader("2. 프로필 수정")

    st.markdown("""
    <div class="success-box">
        인증되었습니다. 프로필을 수정해주세요.
    </div>
    """, unsafe_allow_html=True)

    # TODO: Implement profile update form
    # - Load current member data
    # - Show editable form
    # - Submit changes to API

    st.info("프로필 수정 기능은 곧 구현될 예정입니다.")

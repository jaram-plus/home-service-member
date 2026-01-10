"""User Frontend - Member registration and profile update."""

import streamlit as st

# Page config
st.set_page_config(
    page_title="Jaram Member Service",
    page_icon="🌳",
    layout="centered",
)

# Check for profile update token and redirect
query_params = st.query_params
token = query_params.get("token")
if token:
    # Store token in session state before switching
    st.session_state.profile_token = token
    st.switch_page("pages/02_프로필_수정.py")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        color: #155724;
    }
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.25rem;
        color: #0c5460;
    }
    .welcome-box {
        padding: 2rem;
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 0.5rem;
        text-align: center;
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🌳 자람 (Jaram)</h1>
    <p>동아리 회원가입 및 프로필 관리</p>
</div>
""", unsafe_allow_html=True)

# Welcome content
st.markdown("""
<div class="welcome-box">
    <h2>환영합니다!</h2>
    <p>왼쪽 사이드바에서 메뉴를 선택해주세요.</p>
    <ul style="text-align: left; display: inline-block; margin-top: 1rem;">
        <li><strong>회원가입</strong>: 자람 동아리에 가입하기</li>
        <li><strong>프로필 수정</strong>: 기존 회원정보 수정하기</li>
    </ul>
</div>
""", unsafe_allow_html=True)

st.info("💡 사이드바의 메뉴를 사용하여 페이지를 이동할 수 있습니다.")

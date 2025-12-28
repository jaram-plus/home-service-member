"""User Frontend - Member registration and profile update."""

import os
import streamlit as st

# Page config
st.set_page_config(
    page_title="Jaram Member Service",
    page_icon="🌳",
    layout="centered",
)

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
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🌳 자람 (Jaram)</h1>
    <p>동아리 회원가입 및 프로필 관리</p>
</div>
""", unsafe_allow_html=True)

# Navigation
page = st.radio(
    "메뉴",
    ["회원가입", "프로필 수정"],
    horizontal=True,
    label_visibility="collapsed",
)

if page == "회원가입":
    st.switch_page("pages/01_회원가입.py")
elif page == "프로필 수정":
    st.switch_page("pages/02_프로필_수정.py")

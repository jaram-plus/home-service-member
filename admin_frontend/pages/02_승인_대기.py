"""Pending members approval page."""

import html

import streamlit as st
from utils.api import get_all_members, approve_member, reject_member
from utils.css import load_css

st.set_page_config(
    page_title="Pending Approval - Jaram Admin",
    page_icon="⏳",
    layout="wide",
)

# Load global CSS
load_css()

# Authentication check
if not st.session_state.get("authenticated", False):
    st.error(">> AUTHENTICATION REQUIRED")
    st.switch_page("app.py")

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="padding: 1.5rem 0; margin-bottom: 1rem; border-bottom: 1px solid var(--border-primary);">
        <h2 style="font-size: 1rem; letter-spacing: 0.15em; color: var(--jaram-red);">NAVIGATION</h2>
    </div>
    """, unsafe_allow_html=True)
    page = st.radio(
        "",
        ["Dashboard", "Pending", "Members"],
        index=1,
        label_visibility="collapsed",
    )
    st.markdown("---")
    if st.button("LOGOUT", use_container_width=True, type="secondary"):
        st.session_state.authenticated = False
        st.rerun()

# Page navigation
page_map = {"Dashboard": "dashboard", "Pending": "pending", "Members": "members"}
st.session_state.current_page = page_map[page]

if page == "Dashboard":
    st.switch_page("pages/01_대시보드.py")
elif page == "Members":
    st.switch_page("pages/03_회원_관리.py")

# Page header
st.markdown("""
<div class="page-header">
    <h1 style="font-size: 1.75rem; letter-spacing: 0.1em;">▶ PENDING APPROVALS</h1>
</div>
""", unsafe_allow_html=True)

# Load pending members
try:
    all_members = get_all_members(status="PENDING")
except Exception as e:
    st.error(f">> ERROR: Failed to load data - {str(e)}")
    st.stop()

if not all_members:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon">✓</div>
        <div class="empty-text">NO PENDING APPROVALS</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

st.markdown(f"""
<div class="page-count">>> {len(all_members)} MEMBER(S) AWAITING APPROVAL</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Display each pending member
for i, member in enumerate(all_members):
    member_id = member.get("id")
    name = html.escape(member.get("name", "Unknown"))
    email = html.escape(member.get("email", ""))
    generation = member.get("generation", "-")
    rank = html.escape(member.get("rank", ""))
    description = html.escape(member.get("description", "")) if member.get("description") else ""
    created_at = html.escape(member.get("created_at", "")[:10]) if member.get("created_at") else ""

    st.markdown(f"""
    <div class="pending-card">
        <div class="pending-header">
            <div>
                <div class="member-title">{name}</div>
                <div class="member-subtitle">{email}</div>
            </div>
            <span class="badge badge-pending">PENDING</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("", expanded=(i == 0)):
        st.markdown(f"""
        <div class="pending-body">
            <div class="info-row">
                <span class="info-label">Name</span>
                <span class="info-value">{name}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Email</span>
                <span class="info-value">{email}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Generation</span>
                <span class="info-value">{generation}기</span>
            </div>
            <div class="info-row">
                <span class="info-label">Rank</span>
                <span class="info-value">{rank}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Joined</span>
                <span class="info-value">{created_at}</span>
            </div>
        """, unsafe_allow_html=True)

        if description:
            st.markdown(f"""
            <div class="description-box">
                <div class="description-label">Self Introduction</div>
                <div class="description-text">{description}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # Actions
        col1, col2 = st.columns(2)

        with col1:
            if st.button(
                "✓ APPROVE",
                key=f"approve_{member_id}",
                use_container_width=True,
            ):
                try:
                    approve_member(member_id)
                    st.success(f">> SUCCESS: {name} approved")
                    st.rerun()
                except Exception as e:
                    st.error(f">> ERROR: Approval failed - {e}")

        with col2:
            if st.button(
                "✗ REJECT",
                key=f"reject_{member_id}",
                use_container_width=True,
            ):
                try:
                    reject_member(member_id)
                    st.success(f">> SUCCESS: {name} rejected")
                    st.rerun()
                except Exception as e:
                    st.error(f">> ERROR: Rejection failed - {e}")

    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

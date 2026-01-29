"""Dashboard page - Statistics overview."""

import html

import streamlit as st
from utils.api import get_all_members, MemberStatus
from utils.css import load_css

st.set_page_config(
    page_title="Dashboard - Jaram Admin",
    page_icon="📊",
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
        index=0,
        label_visibility="collapsed",
    )
    st.markdown("---")
    if st.button("LOGOUT", use_container_width=True, type="secondary"):
        st.session_state.authenticated = False
        st.rerun()

# Page navigation
page_map = {"Dashboard": "dashboard", "Pending": "pending", "Members": "members"}
st.session_state.current_page = page_map[page]

if page == "Pending":
    st.switch_page("pages/02_승인_대기.py")
elif page == "Members":
    st.switch_page("pages/03_회원_관리.py")

# Page header
st.markdown("""
<div style="padding: 1.5rem 0; margin-bottom: 2rem; border-bottom: 1px solid var(--border-primary);">
    <h1 style="font-size: 1.75rem; letter-spacing: 0.1em;">▶ DASHBOARD</h1>
</div>
""", unsafe_allow_html=True)

# Load data
try:
    all_members = get_all_members()
    pending_members = [m for m in all_members if m.get("status") == MemberStatus.PENDING]
    approved_members = [m for m in all_members if m.get("status") == MemberStatus.APPROVED]
    unverified_members = [m for m in all_members if m.get("status") == MemberStatus.UNVERIFIED]
except Exception as e:
    st.error(f">> ERROR: Failed to load data - {str(e)}")
    st.stop()

# Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Members</div>
        <div class="metric-value">{len(all_members)}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    alert_class = "alert" if pending_members else ""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Pending Approval</div>
        <div class="metric-value">{len(pending_members)}</div>
        <div class="metric-delta {alert_class}">{'>> ACTION REQUIRED' if pending_members else ''}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Approved</div>
        <div class="metric-value">{len(approved_members)}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Unverified</div>
        <div class="metric-value">{len(unverified_members)}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Two column layout
col1, col2 = st.columns(2)

with col1:
    # Status Distribution
    st.markdown("""
    <div class="recent-section">
        <div class="section-header">▸ STATUS DISTRIBUTION</div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="padding: 0.75rem 0; border-bottom: 1px solid var(--border-primary);">
        <div style="font-family: var(--font-mono); color: var(--accent-yellow);">PENDING</div>
        <div style="font-family: var(--font-mono); font-size: 1.5rem; font-weight: 700; margin-top: 0.25rem;">{len(pending_members)}</div>
    </div>
    <div style="padding: 0.75rem 0; border-bottom: 1px solid var(--border-primary);">
        <div style="font-family: var(--font-mono); color: var(--accent-green);">APPROVED</div>
        <div style="font-family: var(--font-mono); font-size: 1.5rem; font-weight: 700; margin-top: 0.25rem;">{len(approved_members)}</div>
    </div>
    <div style="padding: 0.75rem 0;">
        <div style="font-family: var(--font-mono); color: var(--accent-blue);">UNVERIFIED</div>
        <div style="font-family: var(--font-mono); font-size: 1.5rem; font-weight: 700; margin-top: 0.25rem;">{len(unverified_members)}</div>
    </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    # Recent Signups
    st.markdown("""
    <div class="recent-section">
        <div class="section-header">▸ RECENT SIGNUPS</div>
    """, unsafe_allow_html=True)

    if all_members:
        recent_members = sorted(all_members, key=lambda x: x.get("created_at", ""), reverse=True)[:5]

        status_class_map = {
            MemberStatus.UNVERIFIED: "unverified",
            MemberStatus.PENDING: "pending",
            MemberStatus.APPROVED: "approved",
        }

        for member in recent_members:
            name = html.escape(member.get("name", "Unknown"))
            email = html.escape(member.get("email", ""))
            status = member.get("status", "UNKNOWN")
            status_class = status_class_map.get(status, "")
            status_display = html.escape(status)
            created_at = html.escape(member.get("created_at", "")[:10]) if member.get("created_at") else ""

            st.markdown(f"""
            <div class="member-row">
                <div class="member-name">{name} <span class="badge badge-{status_class}">{status_display}</span></div>
                <div class="member-email">{email}</div>
                <div class="member-date">{created_at}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="padding: 1rem; font-family: var(--font-mono); color: var(--text-muted);">No members yet</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Pending Members Alert
if pending_members:
    st.markdown(f"""
    <div class="alert-section">
        <div class="alert-title">⚠ PENDING APPROVALS</div>
        <div class="alert-message">{len(pending_members)} member(s) awaiting approval. Process them now.</div>
    """, unsafe_allow_html=True)

    if st.button("GO TO PENDING PAGE", use_container_width=True, type="primary"):
        st.switch_page("pages/02_승인_대기.py")

    st.markdown("</div>", unsafe_allow_html=True)

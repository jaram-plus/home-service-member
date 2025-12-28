"""Dashboard page - Statistics overview."""

import streamlit as st
from utils.api import get_all_members

st.set_page_config(
    page_title="대시보드 - Jaram Admin",
    page_icon="📊",
    layout="wide",
)

# Authentication check
if not st.session_state.get("authenticated", False):
    st.error("로그인이 필요합니다.")
    st.switch_page("app.py")

# Sidebar
with st.sidebar:
    st.title("메뉴")
    page = st.radio(
        "Navigation",
        ["대시보드", "승인 대기", "회원 관리"],
        index=0,
    )
    st.markdown("---")
    if st.button("로그아웃", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# Page navigation
if page == "승인 대기":
    st.switch_page("pages/02_승인_대기.py")
elif page == "회원 관리":
    st.switch_page("pages/03_회원_관리.py")

# Update session state for navigation
st.session_state.current_page = "dashboard"

st.title("대시보드")
st.markdown("---")

# Load data
try:
    all_members = get_all_members()
    pending_members = [m for m in all_members if m["status"] == "PENDING"]
    approved_members = [m for m in all_members if m["status"] == "APPROVED"]
    unverified_members = [m for m in all_members if m["status"] == "UNVERIFIED"]
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

# Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("전체 회원", len(all_members))

with col2:
    st.metric(
        "승인 대기",
        len(pending_members),
        delta="처리 필요" if pending_members else "",
        delta_color="inverse" if pending_members else "normal",
    )

with col3:
    st.metric("승인 완료", len(approved_members))

with col4:
    st.metric("미인증", len(unverified_members))

st.markdown("---")

# Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("상태별 분포")
    status_labels = ["승인 대기 (PENDING)", "승인 완료 (APPROVED)", "미인증 (UNVERIFIED)"]
    status_values = [len(pending_members), len(approved_members), len(unverified_members)]

    # Display as simple metrics
    for label, value in zip(status_labels, status_values):
        st.metric(label=label, value=value)

with col2:
    st.subheader("최근 가입")
    if all_members:
        # Sort by created_at
        recent_members = sorted(all_members, key=lambda x: x.get("created_at", ""), reverse=True)[:5]

        for member in recent_members:
            name = member.get("name", "Unknown")
            email = member.get("email", "")
            status = member.get("status", "UNKNOWN")
            created_at = member.get("created_at", "")[:10] if member.get("created_at") else ""

            st.markdown(f"""
            <div style="padding: 0.5rem; border-bottom: 1px solid #eee;">
                <strong>{name}</strong> <span class="status-{status}">({status})</span><br/>
                <small>{email}</small><br/>
                <small style="color: #666;">{created_at}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("가입자가 없습니다.")

st.markdown("---")

# Recent pending members (quick action)
if pending_members:
    st.subheader("⚠️ 승인 대기 중인 회원")
    st.info(f"{len(pending_members)}명의 회원이 승인을 기다리고 있습니다. [승인 대기](pages/02_승인_대기.py) 페이지에서 처리해주세요.")

    if st.button("승인 대기 페이지로 이동", use_container_width=True):
        st.switch_page("pages/02_승인_대기.py")

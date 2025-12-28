"""Pending members approval page."""

import streamlit as st
from utils.api import get_all_members, approve_member, reject_member

st.set_page_config(
    page_title="승인 대기 - Jaram Admin",
    page_icon="⏳",
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
        index=1,
    )
    st.markdown("---")
    if st.button("로그아웃", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# Page navigation
if page == "대시보드":
    st.switch_page("pages/01_대시보드.py")
elif page == "회원 관리":
    st.switch_page("pages/03_회원_관리.py")

# Update session state for navigation
st.session_state.current_page = "pending"

st.title("승인 대기")
st.markdown("---")

# Load pending members
try:
    all_members = get_all_members(status="PENDING")
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

if not all_members:
    st.info("승인 대기 중인 회원이 없습니다.")
    st.stop()

st.success(f"{len(all_members)}명의 회원이 승인을 기다리고 있습니다.")

st.markdown("---")

# Display each pending member
for i, member in enumerate(all_members):
    member_id = member.get("id")
    name = member.get("name", "Unknown")
    email = member.get("email", "")
    generation = member.get("generation", "-")
    rank = member.get("rank", "")
    description = member.get("description", "")
    created_at = member.get("created_at", "")[:10] if member.get("created_at") else ""

    with st.expander(f"📝 {name} ({email}) - {created_at}", expanded=(i == 0)):
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"""
            **이름:** {name}
            **이메일:** {email}
            **기수:** {generation}기
            **계급:** {rank}
            **가입일:** {created_at}
            """)

            if description:
                st.markdown(f"**자기소개:** {description}")

        with col2:
            st.markdown("#### 승인/거절")

            col_btn1, col_btn2 = st.columns(2)

            with col_btn1:
                if st.button(
                    "✅ 승인",
                    key=f"approve_{member_id}",
                    use_container_width=True,
                    type="primary",
                ):
                    try:
                        approve_member(member_id)
                        st.success(f"{name}님을 승인했습니다.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"승인 중 오류가 발생했습니다: {e}")

            with col_btn2:
                if st.button(
                    "❌ 거절",
                    key=f"reject_{member_id}",
                    use_container_width=True,
                ):
                    try:
                        reject_member(member_id)
                        st.success(f"{name}님을 거절했습니다.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"거절 중 오류가 발생했습니다: {e}")

    st.markdown("---")

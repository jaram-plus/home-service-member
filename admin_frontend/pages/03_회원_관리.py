"""All members management page."""

import streamlit as st
from utils.api import get_all_members, delete_member

st.set_page_config(
    page_title="회원 관리 - Jaram Admin",
    page_icon="👥",
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
        index=2,
    )
    st.markdown("---")
    if st.button("로그아웃", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# Page navigation
if page == "대시보드":
    st.switch_page("pages/01_대시보드.py")
elif page == "승인 대기":
    st.switch_page("pages/02_승인_대기.py")

# Update session state for navigation
st.session_state.current_page = "members"

st.title("회원 관리")
st.markdown("---")

# Filters
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    status_filter = st.selectbox(
        "상태 필터",
        options=["전체", "UNVERIFIED", "PENDING", "APPROVED"],
        format_func=lambda x: {
            "전체": "전체",
            "UNVERIFIED": "미인증",
            "PENDING": "승인 대기",
            "APPROVED": "승인 완료",
        }.get(x, x),
    )

with col2:
    search_query = st.text_input("검색 (이름/이메일)", placeholder="검색어 입력...")

with col3:
    st.write("")
    if st.button("새로고침", use_container_width=True):
        st.rerun()

st.markdown("---")

# Load data
try:
    params = {} if status_filter == "전체" else {"status": status_filter}
    all_members = get_all_members(status=params.get("status"))
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

# Apply search filter
if search_query:
    query = search_query.lower()
    all_members = [
        m
        for m in all_members
        if query in m.get("name", "").lower() or query in m.get("email", "").lower()
    ]

if not all_members:
    st.info("표시할 회원이 없습니다.")
    st.stop()

st.info(f"총 {len(all_members)}명")

# Display members in a table format
st.markdown("### 회원 목록")

# Create columns for the table
col_widths = [2, 3, 1, 1, 2, 1]
columns = st.columns(col_widths)

headers = ["이름", "이메일", "기수", "계급", "상태", ""]
for col, header in zip(columns, headers):
    col.write(f"**{header}**")

st.markdown("---")

for member in all_members:
    member_id = member.get("id")
    name = member.get("name", "Unknown")
    email = member.get("email", "")
    generation = member.get("generation", "-")
    rank = member.get("rank", "")
    status = member.get("status", "UNKNOWN")

    cols = st.columns(col_widths)

    with cols[0]:
        st.write(name)

    with cols[1]:
        st.write(email)

    with cols[2]:
        st.write(f"{generation}기" if generation != "-" else "-")

    with cols[3]:
        rank_display = {
            "정회원": "활동",
            "준OB": "예비OB",
            "OB": "OB",
        }.get(rank, rank)
        st.write(rank_display)

    with cols[4]:
        status_color = {
            "PENDING": "🟡",
            "APPROVED": "🟢",
            "UNVERIFIED": "⚪",
        }.get(status, "⚫")
        st.write(f"{status_color} {status}")

    with cols[5]:
        if st.button("삭제", key=f"delete_{member_id}"):
            st.session_state[f"confirm_delete_{member_id}"] = True

    # Confirm delete dialog
    if st.session_state.get(f"confirm_delete_{member_id}"):
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.warning(f"'{name}'님을 정말 삭제하시겠습니까?")
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("확인", key=f"confirm_{member_id}", type="primary"):
                        try:
                            delete_member(member_id)
                            st.success("삭제되었습니다.")
                            st.session_state[f"confirm_delete_{member_id}"] = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"삭제 중 오류가 발생했습니다: {e}")
                with col_btn2:
                    if st.button("취소", key=f"cancel_{member_id}"):
                        st.session_state[f"confirm_delete_{member_id}"] = False
                        st.rerun()

    st.markdown("")

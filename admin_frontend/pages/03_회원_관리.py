"""All members management page."""

import html

import streamlit as st
from utils.api import get_all_members, delete_member
from utils.css import load_css

st.set_page_config(
    page_title="Members - Jaram Admin",
    page_icon="👥",
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
        index=2,
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
elif page == "Pending":
    st.switch_page("pages/02_승인_대기.py")

# Page header
st.markdown("""
<div class="page-header">
    <h1 style="font-size: 1.75rem; letter-spacing: 0.1em;">▶ MEMBERS</h1>
</div>
""", unsafe_allow_html=True)

# Filters
st.markdown("""
<div class="filter-section">
    <div class="filter-row">
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    status_filter = st.selectbox(
        "STATUS_FILTER",
        options=["ALL", "PENDING", "APPROVED", "UNVERIFIED"],
        format_func=lambda x: {
            "ALL": "All Status",
            "UNVERIFIED": "Unverified",
            "PENDING": "Pending",
            "APPROVED": "Approved",
        }.get(x, x),
        label_visibility="collapsed",
    )

with col2:
    search_query = st.text_input(
        "SEARCH",
        placeholder="Search by name or email...",
        label_visibility="collapsed",
    )

with col3:
    if st.button("REFRESH", use_container_width=True, type="secondary"):
        st.rerun()

st.markdown("""
    </div>
</div>
""", unsafe_allow_html=True)

# Load data
try:
    params = None if status_filter == "ALL" else {"status": status_filter}
    all_members = get_all_members(status=params.get("status") if params else None)
except Exception as e:
    st.error(f">> ERROR: Failed to load data - {str(e)}")
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
    st.markdown("""
    <div class="empty-state">
        <div class="empty-text">NO MEMBERS FOUND</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

st.markdown(f"""
<div class="result-info">>> SHOWING {len(all_members)} MEMBER(S)</div>
""", unsafe_allow_html=True)

# Display members table
st.markdown("""
<div class="members-table-container">
    <div class="table-header">
        <div class="table-header-cell">NAME</div>
        <div class="table-header-cell">EMAIL</div>
        <div class="table-header-cell">GEN</div>
        <div class="table-header-cell">RANK</div>
        <div class="table-header-cell">STATUS</div>
        <div class="table-header-cell"></div>
    </div>
""", unsafe_allow_html=True)

for member in all_members:
    member_id = member.get("id")
    name = html.escape(member.get("name", "Unknown"))
    email = html.escape(member.get("email", ""))
    generation = member.get("generation", "-")
    rank = html.escape(member.get("rank", ""))
    status = member.get("status", "UNKNOWN")

    # Format rank
    rank_display = {
        "정회원": "Active",
        "준OB": "Prospective OB",
        "OB": "OB",
    }.get(rank, rank)

    # Format generation
    gen_display = f"{generation}" if generation != "-" else "-"

    # Status badge class
    status_class_map = {
        "PENDING": "pending",
        "APPROVED": "approved",
        "UNVERIFIED": "unverified",
    }
    status_class = status_class_map.get(status, "")

    st.markdown(f"""
    <div class="table-row">
        <div class="table-cell table-cell-name">{name}</div>
        <div class="table-cell table-cell-email">{email}</div>
        <div class="table-cell">{gen_display}</div>
        <div class="table-cell">{rank_display}</div>
        <div class="table-cell"><span class="badge badge-{status_class}">{status}</span></div>
        <div class="table-cell">
    """, unsafe_allow_html=True)

    # Delete button
    delete_key = f"delete_{member_id}"
    if st.button("DELETE", key=delete_key):
        st.session_state[f"confirm_delete_{member_id}"] = True

    st.markdown("""
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
</div>
""", unsafe_allow_html=True)

# Confirm delete dialogs
for member in all_members:
    member_id = member.get("id")
    name = member.get("name", "Unknown")

    if st.session_state.get(f"confirm_delete_{member_id}"):
        st.markdown(f"""
        <div class="confirm-modal">
            <div class="confirm-title">⚠ CONFIRM DELETION</div>
            <div class="confirm-message">
                Are you sure you want to delete <strong>{html.escape(name)}</strong>?<br/>
                <span style="color: var(--text-muted); font-size: 0.85rem;">This action cannot be undone.</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            col_confirm, col_cancel = st.columns(2)

            with col_confirm:
                if st.button("CONFIRM", key=f"confirm_{member_id}", type="primary"):
                    try:
                        delete_member(member_id)
                        st.success(f">> SUCCESS: Member deleted")
                        st.session_state[f"confirm_delete_{member_id}"] = False
                        st.rerun()
                    except Exception as e:
                        st.error(f">> ERROR: Deletion failed - {e}")

            with col_cancel:
                if st.button("CANCEL", key=f"cancel_{member_id}"):
                    st.session_state[f"confirm_delete_{member_id}"] = False
                    st.rerun()

"""Member registration page."""

import streamlit as st

from utils.api import register_member_with_form

st.set_page_config(
    page_title="회원가입 - Jaram",
    page_icon="📝",
    layout="wide",
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
</style>
""", unsafe_allow_html=True)

# Session state for form
if "registration_success" not in st.session_state:
    st.session_state.registration_success = False
if "registered_email" not in st.session_state:
    st.session_state.registered_email = None

# Show success message
if st.session_state.registration_success:
    st.markdown(f"""
    <div class="success-box">
        <h3>가입 신청이 완료되었습니다!</h3>
        <p><strong>{st.session_state.registered_email}</strong>로 인증 이메일을 발송했습니다.</p>
        <p>이메일에 있는 링크를 클릭하여 가입을 완료해주세요.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("다른 사람 가입하기", use_container_width=True):
        st.session_state.registration_success = False
        st.session_state.registered_email = None
        st.rerun()
    st.stop()

# Page title
st.markdown("""
<div class="main-header">
    <h1>🌳 자람 (Jaram) 회원가입</h1>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Basic info section
st.subheader("기본 정보")

col1, col2 = st.columns(2)
with col1:
    name = st.text_input("이름 *", placeholder="홍길동", max_chars=50)
with col2:
    email = st.text_input("이메일 *", placeholder="example@email.com", max_chars=100)

col1, col2 = st.columns(2)
with col1:
    generation = st.number_input("기수 *", min_value=1, max_value=50, value=1, step=1)
with col2:
    rank = st.selectbox("계급 *", options=["정회원", "준OB", "OB"])

description = st.text_area("자기소개", placeholder="간단한 자기소개를 입력해주세요 (선택)", max_chars=500)

st.markdown("---")

# Profile image section
st.subheader("프로필 이미지 (선택)")
image_file = st.file_uploader(
    "프로필 이미지 업로드",
    type=["jpg", "jpeg", "png", "gif", "webp"],
    help="JPG, PNG, GIF, WebP 형식 (최대 5MB)",
)

# Show preview if image is uploaded
if image_file is not None:
    st.image(image_file, caption="업로드된 이미지 미리보기", width=200)

st.markdown("---")

# Skills section
st.subheader("기술 스택 (선택)")
st.caption("쉼표로 구분하여 입력해주세요 (예: Python, React, TypeScript)")
skills_input = st.text_input("스킬", placeholder="Python, React, TypeScript")

st.markdown("---")

# Links section
st.subheader("링크 (선택)")

link_types = {
    "GitHub": "github",
    "LinkedIn": "linkedin",
    "Blog": "blog",
    "Instagram": "instagram",
    "Notion": "notion",
    "백준": "solved_ac",
}

links = []
for label, link_type in link_types.items():
    url = st.text_input(f"{label} URL", key=f"link_{link_type}", placeholder=f"https://...")
    if url:
        links.append({"link_type": link_type, "url": url})

st.markdown("---")

# Submit button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    submitted = st.button("가입 신청", use_container_width=True, type="primary")

if submitted:
    # Validation
    if not name or not email:
        st.error("이름과 이메일을 모두 입력해주세요.")
        st.stop()

    if "@" not in email or "." not in email:
        st.error("올바른 이메일 형식을 입력해주세요.")
        st.stop()

    # Parse skills
    skills = []
    if skills_input:
        skills = [{"skill_name": s.strip()} for s in skills_input.split(",") if s.strip()]

    try:
        register_member_with_form(
            name=name.strip(),
            email=email.strip().lower(),
            generation=generation,
            rank=rank,
            description=description.strip() or "",
            image_file=image_file,
            skills=skills,
            links=links,
        )

        st.session_state.registration_success = True
        st.session_state.registered_email = email.strip().lower()
        st.rerun()

    except Exception as e:
        error_detail = str(e)
        if "already exists" in error_detail.lower() or "unique" in error_detail.lower():
            st.error("이미 가입된 이메일입니다.")
        else:
            st.error(f"가입 중 오류가 발생했습니다: {error_detail}")

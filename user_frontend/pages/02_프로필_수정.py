"""Profile update page with magic link authentication."""

import os
import streamlit as st

from utils.api import request_profile_update_link, verify_profile_update_token, update_member_profile

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
if "profile_token" not in st.session_state:
    st.session_state.profile_token = None
if "profile_member" not in st.session_state:
    st.session_state.profile_member = None
if "profile_update_success" not in st.session_state:
    st.session_state.profile_update_success = False

# URL 쿼리 파라미터 또는 session_state에서 토큰 추출
query_params = st.query_params
token = query_params.get("token") or st.session_state.get("profile_token")

# 토큰이 있으면 자동 인증 시도
if token and not st.session_state.profile_authenticated:
    try:
        with st.spinner("인증 중..."):
            member_data = verify_profile_update_token(token)

        st.session_state.profile_authenticated = True
        st.session_state.profile_token = token
        st.session_state.profile_member = member_data

        # URL에서 토큰 제거 (깔끔하게 만들기)
        query_params.clear()
        st.rerun()

    except Exception as e:
        error_detail = str(e)
        if "expired" in error_detail.lower() or "invalid" in error_detail.lower():
            st.error("인증 토큰이 만료되었거나 유효하지 않습니다. 다시 인증 링크를 요청해주세요.")
        elif "Only approved members" in error_detail:
            st.error("승인된 회원만 프로필을 수정할 수 있습니다.")
        else:
            st.error(f"인증 실패: {error_detail}")

# Step 1: Request magic link
if not st.session_state.profile_authenticated:
    st.subheader("1. 인증 이메일 받기")

    if st.session_state.profile_email_sent:
        st.markdown(f"""
        <div style="padding: 1rem; background-color: #e3f2fd; border-radius: 0.5rem; margin: 1rem 0;">
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

else:
    # Step 2: Profile update form (after authentication)
    st.subheader("2. 프로필 수정")

    member = st.session_state.profile_member

    st.markdown(f"""
    <div style="padding: 1rem; background-color: #e8f5e9; border-radius: 0.5rem; margin: 1rem 0;">
        <p>✅ <strong>{member['email']}</strong>님, 인증되었습니다.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("update_profile"):
        st.markdown("### 기본 정보")

        # 기본 정보
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input(
                "이름",
                value=member.get("name", ""),
                max_chars=50,
                help="이름은 필수 항목입니다."
            )
        with col2:
            # 읽기 전용 필드들
            st.text_input(
                "이메일",
                value=member.get("email", ""),
                disabled=True,
                help="이메일은 변경할 수 없습니다."
            )

        # 기수/직급 (읽기 전용)
        col1, col2 = st.columns(2)
        with col1:
            st.text_input(
                "기수",
                value=str(member.get("generation", "")),
                disabled=True,
                help="기수는 변경할 수 없습니다."
            )
        with col2:
            st.text_input(
                "직급",
                value=member.get("rank", ""),
                disabled=True,
                help="직급은 변경할 수 없습니다."
            )

        # 자기소개
        description = st.text_area(
            "자기소개",
            value=member.get("description", "") or "",
            max_chars=500,
            help="본인에 대해 소개해주세요 (선택)"
        )

        # 프로필 이미지
        image_url = st.text_input(
            "프로필 이미지 URL",
            value=member.get("image_url", "") or "",
            max_chars=500,
            help="프로필 사진의 URL을 입력해주세요 (선택)"
        )

        st.markdown("---")
        st.markdown("### 기술 스택")

        # 기존 스킬 표시
        existing_skills = [s["skill_name"] for s in member.get("skills", [])]
        skills_input = st.text_area(
            "기술 스택",
            value=", ".join(existing_skills),
            help="기술 스택을 쉼표로 구분하여 입력해주세요. 예: Python, React, Docker",
            placeholder="Python, React, Docker"
        )

        st.markdown("---")
        st.markdown("### 링크")

        # 링크 입력
        links_data = member.get("links", [])
        github_url = next((link["url"] for link in links_data if link["link_type"] == "github"), "")
        linkedin_url = next((link["url"] for link in links_data if link["link_type"] == "linkedin"), "")
        etc_url = next((link["url"] for link in links_data if link["link_type"] == "etc"), "")

        col1, col2 = st.columns(2)
        with col1:
            new_github = st.text_input("GitHub", value=github_url, placeholder="https://github.com/username")
            new_linkedin = st.text_input("LinkedIn", value=linkedin_url, placeholder="https://linkedin.com/in/username")
        with col2:
            new_etc = st.text_input("기타 링크", value=etc_url, placeholder="https://...")

        st.markdown("---")

        # 제출 버튼
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button("프로필 수정", use_container_width=True, type="primary")

            if submitted:
                # 필수 필드 validation
                if not name or not name.strip():
                    st.error("이름을 입력해주세요.")
                    st.stop()

                # 스킬 파싱
                skills_list = [
                    {"skill_name": s.strip()}
                    for s in skills_input.split(",")
                    if s.strip()
                ]

                if len(skills_list) > 50:
                    st.error("기술 스택은 50개 이하로 입력해주세요.")
                    st.stop()

                # 링크 파싱
                links_list = []
                if new_github and new_github.strip():
                    links_list.append({"link_type": "github", "url": new_github.strip()})
                if new_linkedin and new_linkedin.strip():
                    links_list.append({"link_type": "linkedin", "url": new_linkedin.strip()})
                if new_etc and new_etc.strip():
                    links_list.append({"link_type": "etc", "url": new_etc.strip()})

                try:
                    with st.spinner("저장 중..."):
                        update_member_profile(
                            member_id=member["id"],
                            token=st.session_state.profile_token,
                            name=name.strip(),
                            description=description.strip() or None,
                            image_url=image_url.strip() or None,
                            skills=skills_list,
                            links=links_list,
                        )

                    # 성공 상태 저장
                    st.session_state.profile_update_success = True
                    st.rerun()

                except Exception as e:
                    error_detail = str(e)
                    if "does not match" in error_detail:
                        st.error("본인의 프로필만 수정할 수 있습니다.")
                    elif "validation" in error_detail.lower():
                        st.error(f"입력값을 확인해주세요: {error_detail}")
                    else:
                        st.error(f"수정 실패: {error_detail}")

# Form 밖: 성공 메시지와 버튼
if st.session_state.profile_update_success:
    st.success("✅ 프로필이 성공적으로 수정되었습니다!")
    st.balloons()

    if st.button("홈으로 가기", use_container_width=True):
        # 세션 초기화
        st.session_state.profile_member = None
        st.session_state.profile_authenticated = False
        st.session_state.profile_token = None
        st.session_state.profile_update_success = False
        st.switch_page("01_회원가입.py")

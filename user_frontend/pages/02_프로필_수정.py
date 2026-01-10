"""Profile update page with magic link authentication."""

import json
import os
import streamlit as st

import requests

from utils.api import request_profile_update_link, update_member_with_image, verify_token

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
if "profile_token" not in st.session_state:
    st.session_state.profile_token = None
if "current_member" not in st.session_state:
    st.session_state.current_member = None

# URL 쿼리 파라미터에서 토큰 추출
query_params = st.query_params
token_from_url = query_params.get("token")

if token_from_url:
    st.session_state.profile_token = token_from_url

# Step 1: Request magic link
if not st.session_state.profile_token:
    st.subheader("1. 인증 이메일 받기")

    if st.session_state.profile_email_sent:
        st.markdown(
            f"""
        <div class="info-box">
            <p><strong>{st.session_state.profile_email}</strong>로 인증 링크를 발송했습니다.</p>
            <p>이메일에 있는 링크를 클릭해주세요.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

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
    # Step 2: Verify token and load member data
    if not st.session_state.current_member:
        try:
            # 토큰 검증
            auth_result = verify_token(st.session_state.profile_token)
            email = auth_result.get("email")

            st.success(f"✅ 인증되었습니다: {email}")

            # 회원 정보 로드 (API 호출 필요 - 임시로 이메일만 표시)
            # 실제로는 GET /members/by-email 또는 유사한 엔드포인트가 필요함
            # 현재는 토큰에서 이메일을 가져온 것으로 대체

            # TODO: 회원 정보를 API에서 로드하는 기능 추가
            st.info("ℹ️  회원 정보 로드 기능은 추가 개발이 필요합니다.")

            st.markdown("---")

            st.subheader("2. 프로필 수정")

            with st.form("profile_update_form"):
                name = st.text_input("이름", value="", help="현재 이름을 입력해주세요")
                rank = st.selectbox("계급", options=["정회원", "준OB", "OB"], index=0)
                description = st.text_area(
                    "자기소개",
                    placeholder="간단한 자기소개를 입력해주세요 (선택)",
                    max_chars=500,
                    help="비워두면 기존 값 유지",
                )

                # Profile image section
                st.markdown("---")
                st.subheader("프로필 이미지 (선택)")
                image_file = st.file_uploader(
                    "새 프로필 이미지를 업로드해주세요",
                    type=["jpg", "jpeg", "png", "webp", "gif"],
                    help="JPG, PNG, WebP, GIF 형식, 최대 5MB. 새 이미지 업로드 시 기존 이미지가 삭제됩니다.",
                )
                if image_file:
                    st.image(image_file, caption="새 이미지", width=200)
                    st.caption(f"파일명: {image_file.name} ({image_file.size / 1024:.1f} KB)")

                # Skills section
                st.markdown("---")
                st.subheader("기술 스택 (선택)")
                st.caption("비워두면 기존 값 유지. 쉼표로 구분하여 입력해주세요.")
                skills_input = st.text_input("스킬", placeholder="Python, React, TypeScript")

                # Links section
                st.markdown("---")
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
                    url = st.text_input(f"{label} URL", key=f"link_{link_type}", placeholder="")
                    if url:
                        links.append({"link_type": link_type, "url": url})

                st.markdown("---")

                submitted = st.form_submit_button("저장", use_container_width=True, type="primary")

                if submitted:
                    # Parse skills
                    skills = []
                    if skills_input.strip():
                        skills = [{"skill_name": s.strip()} for s in skills_input.split(",") if s.strip()]

                    try:
                        # TODO: 실제 member_id 필요 - 현재는 임시 값
                        # 토큰에서 member_id를 가져오거나 별도 API로 조회 필요
                        st.warning("⚠️  실제 저장 기능은 백엔드에서 member_id 조회 후 활성화됩니다.")

                        # 다음과 같이 호출됩니다:
                        # update_member_with_image(
                        #     member_id=member.id,  # 실제 member ID 필요
                        #     token=st.session_state.profile_token,
                        #     name=name if name else None,
                        #     rank=rank,
                        #     description=description if description else None,
                        #     image_file=image_file,
                        #     skills=skills if skills else None,
                        #     links=links if links else None,
                        # )
                        # st.success("✅ 프로필이 업데이트되었습니다!")

                    except Exception as e:
                        error_detail = str(e)
                        if "403" in error_detail or "forbidden" in error_detail.lower():
                            st.error("본인의 프로필만 수정할 수 있습니다.")
                        else:
                            st.error(f"업데이트 실패: {error_detail}")

        except Exception as e:
            st.error(f"인증 실패: {str(e)}")
            st.info("링크가 만료되었을 수 있습니다. 다시 인증 링크를 받아주세요.")

            if st.button("다시 인증하기", use_container_width=True):
                st.session_state.profile_token = None
                st.session_state.profile_email_sent = False
                st.session_state.profile_email = None
                st.rerun()

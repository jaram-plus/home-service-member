def get_magic_link_email_template(magic_link_url: str) -> str:
    """Generate HTML email template for magic link"""
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .button {{
            display: inline-block;
            padding: 12px 24px;
            background-color: #007bff;
            color: white !important;
            text-decoration: none;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>JARAM 홈페이지 인증</h2>
        <p>안녕하세요,</p>
        <p>JARAM 홈페이지에 오신 것을 환영합니다!</p>
        <p>아래 버튼을 클릭하여 인증을 완료해주세요:</p>
        <center>
            <a href="{magic_link_url}" class="button">인증하기</a>
        </center>
        <p>또는 아래 링크를 복사하여 브라우저에 붙여넣으세요:</p>
        <p>{magic_link_url}</p>
        <p>이 링크은 30분간 유효합니다.</p>
        <div class="footer">
            <p>이 이메일은 자동 발송되었습니다. 문의사항이 있으시면 관리자에게 연락해주세요.</p>
        </div>
    </div>
</body>
</html>
"""


def get_approval_email_template(member_name: str) -> str:
    """Generate HTML email template for approval notification"""
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>🎉 가입 승인 완료</h2>
        <p>안녕하세요, {member_name}님</p>
        <p>JARAM 홈페이지 가입이 승인되었습니다.</p>
        <p>이제 홈페이지에서 회원님의 프로필을 확인하실 수 있습니다.</p>
        <div class="footer">
            <p>이 이메일은 자동 발송되었습니다.</p>
        </div>
    </div>
</body>
</html>
"""


def get_rejection_email_template(member_name: str) -> str:
    """Generate HTML email template for rejection notification"""
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>가입 신청 결과</h2>
        <p>안녕하세요, {member_name}님</p>
        <p>죄송하게도 JARAM 홈페이지 가입 신청이 거절되었습니다.</p>
        <p>문의사항이 있으시면 관리자에게 연락해주세요.</p>
        <div class="footer">
            <p>이 이메일은 자동 발송되었습니다.</p>
        </div>
    </div>
</body>
</html>
"""

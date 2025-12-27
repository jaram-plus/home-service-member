from jinja2 import Environment, FileSystemLoader, select_autoescape

# 템플릿 디렉토리 경로
_template_env = Environment(
    loader=FileSystemLoader("templates/email"),
    autoescape=select_autoescape(["html", "xml"]),
)


def render_template(template_name: str, **context) -> str:
    """
    Jinja2 템플릿을 렌더링합니다.

    Args:
        template_name: 템플릿 파일 이름 (예: "magic_link.html")
        **context: 템플릿에 전달할 변수들

    Returns:
        렌더링된 HTML 문자열
    """
    template = _template_env.get_template(template_name)
    return template.render(**context)
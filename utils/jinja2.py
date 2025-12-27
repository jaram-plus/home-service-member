import logging
from pathlib import Path

from jinja2 import (
    Environment,
    FileSystemLoader,
    TemplateError,
    TemplateNotFound,
    UndefinedError,
    select_autoescape,
)

logger = logging.getLogger(__name__)


class TemplateRenderError(Exception):
    """템플릿 렌더링 실패 시 발생하는 예외"""


# 템플릿 디렉토리 경로 (이 파일 위치 기준 절대 경로)
_template_dir = Path(__file__).resolve().parent.parent / "templates" / "email"
_template_env = Environment(
    loader=FileSystemLoader(str(_template_dir)),
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

    Raises:
        TemplateRenderError: 템플릿을 찾을 수 없거나 렌더링에 실패한 경우
            (TemplateNotFound, UndefinedError, TemplateError 등을 감싸서 재발생)
    """
    try:
        template = _template_env.get_template(template_name)
        return template.render(**context)
    except TemplateNotFound as e:
        logger.error(f"Template not found: {template_name} (searched in: {_template_dir})")
        raise TemplateRenderError(f"Template '{template_name}' not found") from e
    except UndefinedError as e:
        logger.error(f"Missing template variable in '{template_name}': {e}")
        raise TemplateRenderError(f"Missing variable in template '{template_name}': {e}") from e
    except TemplateError as e:
        logger.error(f"Template rendering error in '{template_name}': {e}")
        raise TemplateRenderError(f"Failed to render template '{template_name}': {e}") from e
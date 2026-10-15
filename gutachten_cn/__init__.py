"""gutachten-cn：把鉴定式案例分析的方法论编码为可加载、可渲染、可校验的工具。"""

from __future__ import annotations

from .check import check_report, format_result, format_result_md, required_checks
from .practice import render_practice, render_practice_html
from .render import render_outline
from .schemas import default_system, list_systems, load_system, ordered_stages

__version__ = "0.3.0"

__all__ = [
    "list_systems",
    "load_system",
    "default_system",
    "ordered_stages",
    "render_outline",
    "check_report",
    "required_checks",
    "format_result",
    "format_result_md",
    "render_practice",
    "render_practice_html",
    "__version__",
]

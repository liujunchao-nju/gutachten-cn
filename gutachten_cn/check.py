"""校验一份案例分析报告是否遗漏了必需的检视环节。

设计为「提醒」而非「判分」：只要报告中未出现某个必检环节的标题，
就列为缺失，由使用者自行判断是遗漏还是换用了同义表述。
"""

from __future__ import annotations

from .schemas import ordered_stages


def required_checks(system: dict) -> list[tuple[str, str, str]]:
    """返回 (阶层, 检验项, 是否必检) 三元组列表，仅含必检项。"""
    out: list[tuple[str, str, str]] = []
    for stage in ordered_stages(system):
        for chk in stage.get("checks") or []:
            if chk.get("required"):
                out.append((stage["label"], chk["label"], "必检"))
    return out


def _matchable(text: str) -> str:
    """排除 Markdown 表格行后再做匹配。

    说明性表格（如论证深度一览）中提及的要件名并不等于该要件已展开论证，
    若不过滤会把「表格里提了一句」误判为「已覆盖」。
    """
    return "\n".join(
        line for line in text.splitlines() if not line.lstrip().startswith("|")
    )


def check_report(system: dict, text: str) -> dict:
    """比对报告正文与检视程式，输出命中与缺失。"""
    body = _matchable(text)
    found: list[str] = []
    missing: list[str] = []
    for stage_label, chk_label, _ in required_checks(system):
        if chk_label in body:
            found.append(f"{stage_label} / {chk_label}")
        else:
            missing.append(f"{stage_label} / {chk_label}")

    total = len(found) + len(missing)
    coverage = (len(found) / total * 100) if total else 0.0
    return {
        "system": system["system"],
        "label": system["label"],
        "found": found,
        "missing": missing,
        "total_required": total,
        "coverage": round(coverage, 1),
        "complete": not missing,
    }


def format_result(result: dict) -> str:
    lines = [
        f"体系：{result['label']}（{result['system']}）",
        f"必检环节：{result['total_required']} 项，"
        f"命中 {len(result['found'])} 项，"
        f"缺失 {len(result['missing'])} 项，"
        f"覆盖率 {result['coverage']}%",
    ]
    if result["missing"]:
        lines.append("")
        lines.append("缺失环节：")
        for item in result["missing"]:
            lines.append(f"  - {item}")
    else:
        lines.append("")
        lines.append("全部必检环节已覆盖。")
    return "\n".join(lines)

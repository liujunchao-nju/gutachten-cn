"""把检视程式渲染成 Markdown 检视大纲。"""

from __future__ import annotations

from .schemas import ordered_stages


def _source(system: dict) -> str:
    value = system.get("source")
    if not value:
        return ""
    return value.strip() if isinstance(value, str) else str(value)


def render_outline(system: dict, case: dict | None = None) -> str:
    """生成一份可直接填写的检视大纲。

    case 可含 title / case_number / court 等键，用于在大纲头部交代案件。
    """
    lines: list[str] = []
    lines.append(f"# {system['label']}　检视大纲")
    lines.append("")

    if case:
        title = case.get("title") or case.get("case_name")
        if title:
            lines.append(f"**案件**：{title}")
        if case.get("case_number"):
            lines.append(f"**案号**：{case['case_number']}")
        if case.get("court"):
            lines.append(f"**法院**：{case['court']}")
        lines.append("")

    desc = system.get("description")
    if desc:
        lines.append(f"> {str(desc).strip()}")
        lines.append("")

    sub = system.get("subsumption")
    if sub:
        lines.append(f"## 涵摄方法　{sub.get('label', '')}")
        lines.append("")
        for i, step in enumerate(sub.get("steps") or [], 1):
            lines.append(f"{i}. {step}")
        lines.append("")

    for stage in ordered_stages(system):
        order = stage.get("order")
        head = f"{order}　{stage['label']}" if order else stage["label"]
        lines.append(f"## {head}")
        nature = stage.get("nature")
        if nature:
            lines.append("")
            lines.append(f"（{nature}）")
        lines.append("")

        for chk in stage.get("checks") or []:
            required = "必检" if chk.get("required") else "选检"
            lines.append(f"### {chk['label']}　`{required}`")
            lines.append("")
            elements = chk.get("elements") or []
            if elements:
                for el in elements:
                    lines.append(f"- [ ] {el}")
            else:
                lines.append("- [ ] （待补充要件要素）")
            lines.append("")

    src = _source(system)
    if src:
        lines.append("---")
        lines.append("")
        lines.append("**规则依据**")
        lines.append("")
        for line in src.splitlines():
            if line.strip():
                lines.append(line.strip())
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"

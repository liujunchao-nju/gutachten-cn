"""校验一份案例分析报告是否遗漏了必需的检视环节。

匹配分三级证据，由强到弱：

1. **标题命中**：必检环节的名称或其别称出现在 Markdown 标题中，
   是「该环节已独立展开」的最强证据；
2. **正文命中**：出现在正文行（排除 Markdown 表格行）中，
   说明报告提及了该环节，但可能只是一带而过；
3. **缺失**：标题与正文均未出现。

同义词（别称）随检视程式定义在 YAML 的 ``aliases`` 字段中，
与「方法论即数据」的仓库立场一致：新增一套体系或其同义表述，
都不需要改代码。

设计定位仍是「提醒」而非「判分」：缺失仅表示报告中找不到对应环节，
由使用者自行判断是遗漏还是换用了本工具未收录的表述。
"""

from __future__ import annotations

from .schemas import ordered_stages

STATUS_HEADING = "标题"
STATUS_BODY = "正文"
STATUS_MISSING = "缺失"


def required_checks(system: dict) -> list[tuple[str, str, str]]:
    """返回 (阶层, 检验项, 是否必检) 三元组列表，仅含必检项。"""
    out: list[tuple[str, str, str]] = []
    for stage in ordered_stages(system):
        for chk in stage.get("checks") or []:
            if chk.get("required"):
                out.append((stage["label"], chk["label"], "必检"))
    return out


def _aliases(chk: dict) -> list[str]:
    """一个检验项的全部可匹配名称：主名称 + YAML 中声明的别称。"""
    names = [chk["label"]]
    for alias in chk.get("aliases") or []:
        if alias and alias not in names:
            names.append(alias)
    return names


def _headings(text: str) -> list[str]:
    """提取 Markdown 标题行的文字（去掉 # 前缀与首尾空白）。"""
    out = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            out.append(stripped.lstrip("#").strip())
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
    """比对报告正文与检视程式，输出命中与缺失。

    返回 dict 保留既有键（found / missing / coverage / complete），
    并新增 details：每个必检环节的匹配证据明细。
    """
    headings = _headings(text)
    body = _matchable(text)

    details: list[dict] = []
    for stage in ordered_stages(system):
        for chk in stage.get("checks") or []:
            if not chk.get("required"):
                continue
            hit = None
            for alias in _aliases(chk):
                if any(alias in h for h in headings):
                    hit = {"status": STATUS_HEADING, "matched_via": alias, "line": None}
                    break
            if hit is None:
                for lineno, line in enumerate(body.splitlines(), 1):
                    if any(alias in line for alias in _aliases(chk)):
                        hit = {
                            "status": STATUS_BODY,
                            "matched_via": next(
                                a for a in _aliases(chk) if a in line
                            ),
                            "line": lineno,
                        }
                        break
            if hit is None:
                hit = {"status": STATUS_MISSING, "matched_via": None, "line": None}
            details.append(
                {
                    "stage": stage["label"],
                    "check": chk["label"],
                    **hit,
                }
            )

    found = [f"{d['stage']} / {d['check']}" for d in details if d["status"] != STATUS_MISSING]
    missing = [f"{d['stage']} / {d['check']}" for d in details if d["status"] == STATUS_MISSING]

    total = len(details)
    coverage = (len(found) / total * 100) if total else 0.0
    return {
        "system": system["system"],
        "label": system["label"],
        "found": found,
        "missing": missing,
        "details": details,
        "total_required": total,
        "coverage": round(coverage, 1),
        "complete": not missing,
    }


def format_result(result: dict) -> str:
    """纯文本报告（默认输出）。"""
    n_head = sum(1 for d in result["details"] if d["status"] == STATUS_HEADING)
    n_body = sum(1 for d in result["details"] if d["status"] == STATUS_BODY)
    lines = [
        f"体系：{result['label']}（{result['system']}）",
        f"必检环节：{result['total_required']} 项，"
        f"标题命中 {n_head} 项，正文命中 {n_body} 项，"
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


def format_result_md(result: dict) -> str:
    """Markdown 报告，便于留档或贴进 issue。"""
    n_head = sum(1 for d in result["details"] if d["status"] == STATUS_HEADING)
    n_body = sum(1 for d in result["details"] if d["status"] == STATUS_BODY)
    lines = [
        f"# 检视校验报告：{result['label']}",
        "",
        f"- 体系：`{result['system']}`",
        f"- 必检环节：{result['total_required']} 项"
        f"（标题命中 {n_head} / 正文命中 {n_body} / 缺失 {len(result['missing'])}）",
        f"- 覆盖率：{result['coverage']}%",
        "",
        "| 阶层 | 必检环节 | 结果 | 命中方式 |",
        "|---|---|---|---|",
    ]
    for d in result["details"]:
        via = d["matched_via"] or "-"
        lines.append(f"| {d['stage']} | {d['check']} | {d['status']} | {via} |")
    lines.append("")
    if result["missing"]:
        lines.append("**缺失环节**：")
        lines.append("")
        for item in result["missing"]:
            lines.append(f"- {item}")
    else:
        lines.append("全部必检环节已覆盖。")
    lines.append("")
    lines.append("> 本报告仅作提醒，不判分；缺失可能是遗漏，也可能是换用了未收录的同义表述。")
    return "\n".join(lines)

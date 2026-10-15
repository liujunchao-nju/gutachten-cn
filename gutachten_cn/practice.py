"""练习模式：只给检视提示，不给完整大纲。

与 ``outline`` 的分工：outline 是**答案侧的脚手架**（列出全部要件要素），
practice 是**提问侧的练习卷**：只交代每个必检环节的名称、设问与「本环节
含几个要件要素」，不列要素内容，避免练习者直接照抄大纲。

练习流程：先在 practice 卷上独立作答，再用 ``outline`` 对照完整大纲自评。
成稿自查清单取自 ``proportionality`` 体系的 ``self_check`` 阶层
（该数据缺失时退化为内置的通用自查项），同样是数据驱动。
"""

from __future__ import annotations

from .render import _esc
from .schemas import list_systems, load_system, ordered_stages

_FALLBACK_SELF_CHECK = [
    "是否对每个要件都做了层级判断",
    "有无将争议要素错误归入第一层（漏写）",
    "有无将显然要素错误归入第三层（堆料）",
    "第二层要素是否均完成涵摄四步法",
    "第三层要素是否包含法律解释＋学说展开＋反对说回应",
    "立场选择是否给出积极理由，整篇是否贯彻同一立场",
]

_INTEGRITY_NOTE = (
    "学术诚信：本卷用于方法论训练。请先独立完成作答，再对照完整大纲自评；"
    "不得将本工具产出直接作为本人课程作业或考试答案提交。"
)


def _self_check_items() -> list[str]:
    """优先取 proportionality 体系的自查清单；取不到则用内置兜底。"""
    try:
        system = load_system("proportionality")
    except KeyError:
        return list(_FALLBACK_SELF_CHECK)
    for stage in ordered_stages(system):
        if stage.get("id") == "self_check":
            for chk in stage.get("checks") or []:
                elements = chk.get("elements") or []
                if elements:
                    return [str(e) for e in elements]
    return list(_FALLBACK_SELF_CHECK)


def render_practice(system: dict, case: dict | None = None) -> str:
    """生成一份练习卷（Markdown）。"""
    lines: list[str] = []
    lines.append(f"# {system['label']}　练习卷")
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

    lines.append("> 本卷只提示必检环节，不列要件要素。请先自行穷尽各环节的要点，"
                 "再用 `outline` 生成完整大纲对照自评。")
    lines.append("")

    sub = system.get("subsumption")
    if sub:
        lines.append(f"## 涵摄方法提示　{sub.get('label', '')}")
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
            lines.append(f"**设问**：本案中，「{chk['label']}」是否成立？"
                         "请列出你的判断、依据与理由。")
            lines.append("")
            n = len(chk.get("elements") or [])
            if required and n:
                lines.append(f"- 本环节含 {n} 个要件要素，请自行穷尽后与完整大纲核对。")
            elif required:
                lines.append("- 本环节的要件要素请自行检索法条后列出。")
            else:
                lines.append("- 选检环节：结合案情判断是否需要展开。")
            lines.append("")
            lines.append("作答：")
            lines.append("")
            lines.append("（此处留白，供书面或电子作答）")
            lines.append("")

    lines.append("## 成稿自查清单")
    lines.append("")
    for item in _self_check_items():
        lines.append(f"- [ ] {item}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(_INTEGRITY_NOTE)
    lines.append("")
    return "\n".join(lines)


def render_practice_html(system: dict, case: dict | None = None) -> str:
    """练习卷的 HTML 版（可打印后手写作答）。"""
    title = f"{system['label']}　练习卷"
    parts: list[str] = [
        "<!DOCTYPE html>",
        '<html lang="zh-CN">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{_esc(title)}</title>",
        "<style>",
        ":root { color-scheme: light; }",
        "* { box-sizing: border-box; }",
        'body { font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;',
        "  max-width: 860px; margin: 2rem auto; padding: 0 1.2rem; color: #1a1a1a;",
        "  background: #fafaf8; line-height: 1.65; }",
        "h1 { font-size: 1.5rem; border-bottom: 2px solid #1f4e79; padding-bottom: .4rem; }",
        "h2 { font-size: 1.15rem; margin-top: 2rem; color: #16385a; }",
        "h3 { font-size: 1rem; margin-top: 1.2rem; }",
        "blockquote { border-left: 3px solid #9db8d2; margin: .6rem 0; padding: .2rem 1rem;",
        "  color: #555; background: #fff; }",
        ".nature { color: #8a6d3b; font-size: .9rem; }",
        ".tag { display: inline-block; font-size: .75rem; border-radius: 4px;",
        "  padding: 0 .4rem; margin-left: .5rem; vertical-align: middle; }",
        ".tag-required { background: #1f4e79; color: #fff; }",
        ".tag-optional { background: #e8e2d5; color: #6b5f4e; }",
        ".hint { font-size: .9rem; color: #6b5f4e; }",
        ".answer { border: 1px solid #d8d2c4; border-radius: 6px; min-height: 5.5rem;",
        "  margin: .4rem 0 1rem; background: #fff repeating-linear-gradient(",
        "  transparent, transparent 1.7rem, #eef 1.7rem, #eef calc(1.7rem + 1px)); }",
        ".meta { background: #fff; border: 1px solid #e3ddd2; border-radius: 8px;",
        "  padding: .8rem 1rem; }",
        ".meta dl { display: grid; grid-template-columns: auto 1fr; gap: .2rem .8rem; margin: 0; }",
        ".meta dt { font-weight: 600; color: #6b5f4e; }",
        ".meta dd { margin: 0; }",
        "footer { margin-top: 2.5rem; font-size: .8rem; color: #999; }",
        "</style>",
        "</head>",
        "<body>",
        f"<h1>{_esc(title)}</h1>",
        "<blockquote>本卷只提示必检环节，不列要件要素。请先自行穷尽各环节的要点，"
        "再用 outline 生成完整大纲对照自评。</blockquote>",
    ]

    if case:
        rows: list[str] = []
        c_title = case.get("title") or case.get("case_name")
        if c_title:
            rows.append(f"<dt>案件</dt><dd>{_esc(c_title)}</dd>")
        if case.get("case_number"):
            rows.append(f"<dt>案号</dt><dd>{_esc(case['case_number'])}</dd>")
        if case.get("court"):
            rows.append(f"<dt>法院</dt><dd>{_esc(case['court'])}</dd>")
        if rows:
            parts.append(f'<div class="meta"><dl>{"".join(rows)}</dl></div>')

    for stage in ordered_stages(system):
        order = stage.get("order")
        head = f"{order}　{stage['label']}" if order else stage["label"]
        parts.append(f"<h2>{_esc(head)}</h2>")
        nature = stage.get("nature")
        if nature:
            parts.append(f'<div class="nature">（{_esc(nature)}）</div>')
        for chk in stage.get("checks") or []:
            required = chk.get("required")
            tag = ('<span class="tag tag-required">必检</span>' if required
                   else '<span class="tag tag-optional">选检</span>')
            parts.append(f"<h3>{_esc(chk['label'])}{tag}</h3>")
            parts.append(
                f"<p><strong>设问</strong>：本案中，「{_esc(chk['label'])}」是否成立？"
                "请列出你的判断、依据与理由。</p>"
            )
            n = len(chk.get("elements") or [])
            if required and n:
                parts.append(f'<p class="hint">本环节含 {n} 个要件要素，'
                             "请自行穷尽后与完整大纲核对。</p>")
            elif required:
                parts.append('<p class="hint">本环节的要件要素请自行检索法条后列出。</p>')
            else:
                parts.append('<p class="hint">选检环节：结合案情判断是否需要展开。</p>')
            parts.append('<div class="answer"></div>')

    parts.append("<h2>成稿自查清单</h2>")
    parts.append('<ul class="checklist">')
    for item in _self_check_items():
        parts.append(f"<li>{_esc(item)}</li>")
    parts.append("</ul>")
    parts.append(f"<footer>{_esc(_INTEGRITY_NOTE)}</footer>")
    parts.append("</body>")
    parts.append("</html>")
    return "\n".join(parts)


def available_systems() -> list[str]:
    """全部体系名，供 CLI 报错时提示。"""
    return [s["system"] for s in list_systems()]

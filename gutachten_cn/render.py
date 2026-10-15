"""把检视程式渲染成检视大纲。

支持两种格式：

- ``md``：Markdown，可勾选清单（``- [ ]``），可直接粘贴进笔记软件；
- ``html``：零依赖单文件 HTML，内联 CSS 与少量 JS，离线可开，
  带勾选进度条，适合直接发给协作者或在浏览器里边读边勾。
"""

from __future__ import annotations

import html as _html

from .schemas import ordered_stages

FORMATS = ("md", "html")


def _source(system: dict) -> str:
    value = system.get("source")
    if not value:
        return ""
    return value.strip() if isinstance(value, str) else str(value)


def _esc(text: str) -> str:
    return _html.escape(str(text), quote=True)


def render_outline(system: dict, case: dict | None = None, fmt: str = "md") -> str:
    """生成一份可直接填写的检视大纲。

    case 可含 title / case_number / court 等键，用于在大纲头部交代案件。
    fmt 取 ``md``（默认）或 ``html``。
    """
    if fmt == "html":
        return _render_html(system, case)
    if fmt != "md":
        raise ValueError(f"不支持的格式: {fmt}；可用: {', '.join(FORMATS)}")
    return _render_md(system, case)


def _render_md(system: dict, case: dict | None) -> str:
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


_CSS = """
:root { color-scheme: light; }
* { box-sizing: border-box; }
body { font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
  max-width: 860px; margin: 2rem auto; padding: 0 1.2rem; color: #1a1a1a;
  background: #fafaf8; line-height: 1.65; }
h1 { font-size: 1.5rem; border-bottom: 2px solid #8b0000; padding-bottom: .4rem; }
h2 { font-size: 1.15rem; margin-top: 2rem; color: #5c1010; }
h3 { font-size: 1rem; margin-top: 1.2rem; }
.meta { background: #fff; border: 1px solid #e3ddd2; border-radius: 8px;
  padding: .8rem 1rem; }
.meta dl { display: grid; grid-template-columns: auto 1fr; gap: .2rem .8rem; margin: 0; }
.meta dt { font-weight: 600; color: #6b5f4e; }
.meta dd { margin: 0; }
blockquote { border-left: 3px solid #c9b896; margin: .6rem 0; padding: .2rem 1rem;
  color: #555; background: #fff; }
.nature { color: #8a6d3b; font-size: .9rem; }
.tag { display: inline-block; font-size: .75rem; border-radius: 4px;
  padding: 0 .4rem; margin-left: .5rem; vertical-align: middle; }
.tag-required { background: #8b0000; color: #fff; }
.tag-optional { background: #e8e2d5; color: #6b5f4e; }
ul.checklist { list-style: none; padding-left: .2rem; }
ul.checklist li { margin: .25rem 0; }
.progress { position: sticky; top: 0; background: #fafaf8; padding: .6rem 0;
  border-bottom: 1px solid #e3ddd2; z-index: 1; }
.progress progress { width: 100%; height: .8rem; }
.source { font-size: .9rem; background: #fff; border: 1px dashed #c9b896;
  border-radius: 8px; padding: .6rem 1rem; white-space: pre-wrap; }
footer { margin-top: 2.5rem; font-size: .8rem; color: #999; }
"""

_JS = """
document.querySelectorAll('input[type=checkbox]').forEach(function (cb) {
  cb.addEventListener('change', update);
});
function update() {
  var boxes = Array.prototype.slice.call(
    document.querySelectorAll('ul.checklist input[type=checkbox]'));
  var done = boxes.filter(function (b) { return b.checked; }).length;
  var bar = document.querySelector('progress');
  if (bar) { bar.value = done; bar.max = boxes.length; }
  var label = document.getElementById('progress-label');
  if (label) { label.textContent = '已完成 ' + done + ' / ' + boxes.length + ' 项'; }
}
update();
"""


def _render_html(system: dict, case: dict | None) -> str:
    title = f"{system['label']}　检视大纲"
    parts: list[str] = []
    parts.append("<!DOCTYPE html>")
    parts.append('<html lang="zh-CN">')
    parts.append("<head>")
    parts.append('<meta charset="utf-8">')
    parts.append('<meta name="viewport" content="width=device-width, initial-scale=1">')
    parts.append(f"<title>{_esc(title)}</title>")
    parts.append(f"<style>{_CSS}</style>")
    parts.append("</head>")
    parts.append("<body>")
    parts.append(f"<h1>{_esc(title)}</h1>")

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

    desc = system.get("description")
    if desc:
        parts.append(f"<blockquote>{_esc(str(desc).strip())}</blockquote>")

    parts.append('<div class="progress"><progress value="0" max="0"></progress> '
                 '<span id="progress-label"></span></div>')

    sub = system.get("subsumption")
    if sub:
        parts.append(f"<h2>涵摄方法　{_esc(sub.get('label', ''))}</h2>")
        parts.append("<ol>")
        for step in sub.get("steps") or []:
            parts.append(f"<li>{_esc(step)}</li>")
        parts.append("</ol>")

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
            elements = chk.get("elements") or []
            if elements:
                parts.append('<ul class="checklist">')
                for el in elements:
                    parts.append(f'<li><label><input type="checkbox"> {_esc(el)}</label></li>')
                parts.append("</ul>")
            else:
                parts.append('<ul class="checklist"><li><label>'
                             '<input type="checkbox"> （待补充要件要素）'
                             "</label></li></ul>")

    src = _source(system)
    if src:
        parts.append(f'<div class="source">{_esc(src)}</div>')

    parts.append("<footer>由 gutachten-cn 生成 · 方法论即数据 · 仅供学习训练，不构成法律意见</footer>")
    parts.append(f"<script>{_JS}</script>")
    parts.append("</body>")
    parts.append("</html>")
    return "\n".join(parts)

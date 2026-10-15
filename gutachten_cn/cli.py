"""命令行入口。"""

from __future__ import annotations

import argparse
import json
import sys

from .check import check_report, format_result, format_result_md
from .practice import render_practice, render_practice_html
from .render import FORMATS, render_outline
from .schemas import default_system, list_systems, load_system

__all__ = ["main"]


def _write(text: str, out: str | None) -> None:
    if out:
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"已写入 {out}", file=sys.stderr)
    else:
        sys.stdout.write(text)


def _load_case(path: str | None) -> dict | None:
    if not path:
        return None
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _cmd_list(args) -> int:
    systems = list_systems()
    width = max(len(s["system"]) for s in systems)
    for s in systems:
        mark = "（默认）" if s.get("default") else ""
        print(f"{s['system'].ljust(width)}  {s['label']}{mark}　[{s.get('domain', '')}]")
    return 0


def _cmd_show(args) -> int:
    system = load_system(args.system)
    print(f"体系: {system['system']}")
    print(f"名称: {system['label']}")
    print(f"领域: {system.get('domain', '')}")
    print(f"文件: {system['_file']}")
    print(f"默认: {system.get('default', False)}")
    desc = system.get("description")
    if desc:
        print(f"说明: {str(desc).strip()}")
    src = system.get("source")
    if src:
        print("依据:")
        for line in str(src).strip().splitlines():
            if line.strip():
                print(f"  {line.strip()}")
    return 0


def _cmd_outline(args) -> int:
    system = load_system(args.system) if args.system else default_system(args.domain)
    case = _load_case(args.case)
    _write(render_outline(system, case, fmt=args.format), args.out)
    return 0


def _cmd_check(args) -> int:
    system = load_system(args.system) if args.system else default_system(args.domain)
    with open(args.file, encoding="utf-8") as fh:
        text = fh.read()
    result = check_report(system, text)
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.format == "md":
        _write(format_result_md(result), args.out)
    else:
        _write(format_result(result), args.out)
    return 0 if result["complete"] else 1


def _cmd_practice(args) -> int:
    system = load_system(args.system) if args.system else default_system(args.domain)
    case = _load_case(args.case)
    if args.format == "html":
        _write(render_practice_html(system, case), args.out)
    else:
        _write(render_practice(system, case), args.out)
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="gutachten-cn",
        description="鉴定式案例分析：刑法阶层检验与民法请求权基础检索",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="列出全部检视体系").set_defaults(func=_cmd_list)

    show = sub.add_parser("show", help="查看某体系的说明与规则依据")
    show.add_argument("--system", required=True)
    show.set_defaults(func=_cmd_show)

    outline = sub.add_parser("outline", help="生成检视大纲")
    outline.add_argument("--system", help="检视体系；缺省用默认体系")
    outline.add_argument("--domain", help="criminal / civil / administrative，与 --system 二选一")
    outline.add_argument("--case", help="案件信息 JSON 文件")
    outline.add_argument(
        "--format",
        choices=FORMATS,
        default="md",
        help="输出格式：md（默认，可勾选清单）或 html（零依赖单文件）",
    )
    outline.add_argument("--out", help="写入文件；缺省打印到标准输出")
    outline.set_defaults(func=_cmd_outline)

    check = sub.add_parser("check", help="校验报告是否遗漏必检环节")
    check.add_argument("--file", required=True, help="待校验的 Markdown 报告")
    check.add_argument("--system")
    check.add_argument("--domain")
    check.add_argument(
        "--format",
        choices=["text", "json", "md"],
        default="text",
        help="输出格式：text（默认）/ json / md（可留档的报告）",
    )
    check.add_argument("--out", help="写入文件（md 格式时常用）")
    check.set_defaults(func=_cmd_check)

    practice = sub.add_parser("practice", help="生成练习卷：只给检视提示，不给完整大纲")
    practice.add_argument("--system", help="检视体系；缺省用默认体系")
    practice.add_argument("--domain", help="criminal / civil / administrative")
    practice.add_argument("--case", help="案件信息 JSON 文件")
    practice.add_argument(
        "--format",
        choices=["md", "html"],
        default="md",
        help="输出格式：md（默认）或 html（可打印手写）",
    )
    practice.add_argument("--out", help="写入文件；缺省打印到标准输出")
    practice.set_defaults(func=_cmd_practice)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

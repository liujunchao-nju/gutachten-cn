"""命令行入口。"""

from __future__ import annotations

import argparse
import json
import sys

from .check import check_report, format_result
from .render import render_outline
from .schemas import default_system, list_systems, load_system

__all__ = ["main"]


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
    case = None
    if args.case:
        with open(args.case, encoding="utf-8") as fh:
            case = json.load(fh)
    sys.stdout.write(render_outline(system, case))
    return 0


def _cmd_check(args) -> int:
    system = load_system(args.system) if args.system else default_system(args.domain)
    with open(args.file, encoding="utf-8") as fh:
        text = fh.read()
    print(format_result(check_report(system, text)))
    return 0 if check_report(system, text)["complete"] else 1


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
    outline.add_argument("--domain", help="criminal 或 civil，与 --system 二选一")
    outline.add_argument("--case", help="案件信息 JSON 文件")
    outline.set_defaults(func=_cmd_outline)

    check = sub.add_parser("check", help="校验报告是否遗漏必检环节")
    check.add_argument("--file", required=True, help="待校验的 Markdown 报告")
    check.add_argument("--system")
    check.add_argument("--domain")
    check.set_defaults(func=_cmd_check)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

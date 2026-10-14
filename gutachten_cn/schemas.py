"""检视程式加载。

所有方法论写在 schemas/*.yaml 中，本模块只负责读取与校验。
新增一套检视体系不需要改代码，放一个 YAML 文件即可。
"""

from __future__ import annotations

import pathlib

import yaml

SCHEMAS_DIR = pathlib.Path(__file__).parent / "schemas"

REQUIRED_KEYS = ("system", "label", "stages")


class SchemaError(ValueError):
    """检视程式文件不合法。"""


def _read(path: pathlib.Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)
    if not isinstance(doc, dict):
        raise SchemaError(f"{path.name} 内容必须是映射")
    return doc


def list_systems() -> list[dict]:
    """返回全部检视体系，按 domain 与 system 排序。"""
    systems: list[dict] = []
    for path in sorted(SCHEMAS_DIR.rglob("*.yaml")):
        doc = _read(path)
        missing = [k for k in REQUIRED_KEYS if k not in doc]
        if missing:
            raise SchemaError(f"{path.name} 缺少必要字段: {', '.join(missing)}")
        if not isinstance(doc["stages"], list) or not doc["stages"]:
            raise SchemaError(f"{path.name} 的 stages 必须是非空列表")
        doc["_file"] = str(path.relative_to(SCHEMAS_DIR))
        systems.append(doc)
    if not systems:
        raise SchemaError(f"没有找到任何检视程式: {SCHEMAS_DIR}")
    return sorted(systems, key=lambda d: (d.get("domain", ""), d["system"]))


def load_system(name: str) -> dict:
    """按 system 标识加载一套检视体系。"""
    for system in list_systems():
        if system["system"] == name:
            return system
    available = ", ".join(s["system"] for s in list_systems())
    raise KeyError(f"未知的检视体系: {name}；可用: {available}")


def default_system(domain: str | None = None) -> dict:
    """返回默认体系；同域内 default:true 优先，否则取该域第一个。"""
    systems = list_systems()
    if domain:
        systems = [s for s in systems if s.get("domain") == domain] or systems
    for system in systems:
        if system.get("default"):
            return system
    return systems[0]


def ordered_stages(system: dict) -> list[dict]:
    """按 order 字段排序阶层。"""
    return sorted(system["stages"], key=lambda s: s.get("order", 999))

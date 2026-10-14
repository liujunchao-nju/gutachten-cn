"""检视程式的加载、渲染与校验测试。

两篇范文（examples/ 下的公开案例）作为回归基准：
它们覆盖了各自体系的全部必检环节，一旦程式被误改或范文被截断，测试即失败。
"""

from __future__ import annotations

import pathlib

import pytest

from gutachten_cn import (
    check_report,
    default_system,
    list_systems,
    load_system,
    render_outline,
)

ROOT = pathlib.Path(__file__).resolve().parent.parent
CRIMINAL_SAMPLE = ROOT / "examples" / "criminal_sample.md"
CIVIL_SAMPLE = ROOT / "examples" / "civil_sample.md"

EXPECTED_SYSTEMS = {"three-tier", "two-tier", "four-element", "claim-basis"}


def test_all_systems_are_loadable():
    names = {s["system"] for s in list_systems()}
    assert names == EXPECTED_SYSTEMS


@pytest.mark.parametrize("name", sorted(EXPECTED_SYSTEMS))
def test_system_has_required_metadata(name):
    system = load_system(name)
    assert system["label"]
    assert system.get("domain") in {"criminal", "civil"}
    assert system.get("source"), f"{name} 必须写规则依据"
    assert system["stages"]


def test_default_systems():
    assert default_system("criminal")["system"] == "three-tier"
    assert default_system("civil")["system"] == "claim-basis"


@pytest.mark.parametrize("name", sorted(EXPECTED_SYSTEMS))
def test_outline_contains_every_required_check(name):
    system = load_system(name)
    outline = render_outline(system)
    for stage in system["stages"]:
        for chk in stage.get("checks") or []:
            if chk.get("required"):
                assert chk["label"] in outline, f"{name} 大纲缺少 {chk['label']}"


def test_outline_renders_case_metadata():
    system = default_system("criminal")
    text = render_outline(system, {
        "title": "朱某盗窃案",
        "case_number": "（2025）沪0117刑初373号",
        "court": "上海市松江区人民法院",
    })
    assert "朱某盗窃案" in text
    assert "（2025）沪0117刑初373号" in text


def test_criminal_sample_covers_three_tier():
    """刑法范文须覆盖三阶层的全部必检环节。"""
    result = check_report(load_system("three-tier"), CRIMINAL_SAMPLE.read_text(encoding="utf-8"))
    assert result["complete"], f"缺失环节: {result['missing']}"


def test_civil_sample_covers_claim_basis():
    """民法范文须覆盖请求权基础七步的全部必检环节。"""
    result = check_report(load_system("claim-basis"), CIVIL_SAMPLE.read_text(encoding="utf-8"))
    assert result["complete"], f"缺失环节: {result['missing']}"


def test_check_reports_missing_when_stage_removed():
    text = CRIMINAL_SAMPLE.read_text(encoding="utf-8")
    # 删去「有责性」整节，校验应当报出该阶层的必检项缺失
    truncated = text.split("## 五、事实单元二：有责性")[0]
    result = check_report(load_system("three-tier"), truncated)
    assert not result["complete"]
    assert any("责任能力" in m for m in result["missing"])
    assert result["coverage"] < 100


def test_claim_basis_order_is_declared():
    """请求权检索顺序是本体系的核心，顺序必须明确且稳定。"""
    system = load_system("claim-basis")
    checks = system["stages"][0]["checks"]
    order = [c["id"] for c in checks]
    assert order == [
        "contract",
        "quasi_contract",
        "negotiorum_gestio",
        "property",
        "unjust_enrichment",
        "tort",
        "others",
    ]


def test_unknown_system_raises():
    with pytest.raises(KeyError):
        load_system("not-a-system")

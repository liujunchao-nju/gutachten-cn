"""检视程式的加载、渲染、练习与校验测试。

两篇基础范文（examples/ 下的公开案例）作为回归基准：
它们覆盖了各自体系的全部必检环节，一旦程式被误改或范文被截断，测试即失败。
四篇新增范文（theft / tort / contract / admin）分别锚定对应专门程式。
"""

from __future__ import annotations

import json
import pathlib

import pytest

from gutachten_cn import (
    check_report,
    default_system,
    format_result,
    format_result_md,
    list_systems,
    load_system,
    render_outline,
    render_practice,
    render_practice_html,
)

ROOT = pathlib.Path(__file__).resolve().parent.parent
CRIMINAL_SAMPLE = ROOT / "examples" / "criminal_sample.md"
CIVIL_SAMPLE = ROOT / "examples" / "civil_sample.md"

EXPECTED_SYSTEMS = {
    "three-tier",
    "two-tier",
    "four-element",
    "claim-basis",
    "examination-sequence",
    "crime-forms",
    "proportionality",
    "offense-theft",
    "offense-fraud",
    "offense-homicide",
    "offense-misappropriation",
    "contract-claim",
    "tort-claim",
    "property-claim",
    "unjust-enrichment",
    "negotiorum",
    "administrative-legality",
}

SAMPLE_TARGETS = {
    "theft_sample.md": "offense-theft",
    "tort_sample.md": "tort-claim",
    "contract_sample.md": "contract-claim",
    "admin_sample.md": "administrative-legality",
}


def test_all_systems_are_loadable():
    names = {s["system"] for s in list_systems()}
    assert names == EXPECTED_SYSTEMS


@pytest.mark.parametrize("name", sorted(EXPECTED_SYSTEMS))
def test_system_has_required_metadata(name):
    system = load_system(name)
    assert system["label"]
    assert system.get("domain") in {"criminal", "civil", "administrative", "shared"}
    assert system.get("source"), f"{name} 必须写规则依据"
    assert system.get("version"), f"{name} 必须声明版本"
    assert system["stages"]


def test_default_systems():
    assert default_system("criminal")["system"] == "three-tier"
    assert default_system("civil")["system"] == "claim-basis"
    assert default_system("administrative")["system"] == "administrative-legality"


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


def test_outline_html_is_self_contained():
    html = render_outline(load_system("three-tier"), fmt="html")
    assert html.startswith("<!DOCTYPE html>")
    assert 'type="checkbox"' in html
    assert "<script>" in html
    # 零外部资源：不引用任何 http(s) 链接
    assert "http://" not in html
    assert "https://" not in html


def test_outline_rejects_unknown_format():
    with pytest.raises(ValueError):
        render_outline(load_system("three-tier"), fmt="pdf")


def test_criminal_sample_covers_three_tier():
    """刑法范文须覆盖三阶层的全部必检环节。"""
    result = check_report(load_system("three-tier"), CRIMINAL_SAMPLE.read_text(encoding="utf-8"))
    assert result["complete"], f"缺失环节: {result['missing']}"


def test_civil_sample_covers_claim_basis():
    """民法范文须覆盖请求权基础七步的全部必检环节。"""
    result = check_report(load_system("claim-basis"), CIVIL_SAMPLE.read_text(encoding="utf-8"))
    assert result["complete"], f"缺失环节: {result['missing']}"


@pytest.mark.parametrize("filename,system_name", sorted(SAMPLE_TARGETS.items()))
def test_new_samples_cover_their_systems(filename, system_name):
    """四篇新增范文须各自覆盖对应程式的全部必检环节。"""
    text = (ROOT / "examples" / filename).read_text(encoding="utf-8")
    result = check_report(load_system(system_name), text)
    assert result["complete"], f"{filename} 缺失环节: {result['missing']}"


def test_check_reports_missing_when_stage_removed():
    text = CRIMINAL_SAMPLE.read_text(encoding="utf-8")
    # 删去「有责性」整节，校验应当报出该阶层的必检项缺失
    truncated = text.split("## 五、事实单元二：有责性")[0]
    result = check_report(load_system("three-tier"), truncated)
    assert not result["complete"]
    assert any("责任能力" in m for m in result["missing"])
    assert result["coverage"] < 100


def test_check_matches_declared_alias():
    """同义表述按 YAML 中声明的 aliases 命中，不应误判缺失。"""
    system = load_system("three-tier")
    text = "## 分析\n\n本案不存在正当化事由，亦无责任阻却事由。\n"
    result = check_report(system, text)
    assert not any("违法阻却事由" in m for m in result["missing"])


def test_check_table_mention_is_not_coverage():
    """只在表格行中出现的要件名，不视为已展开论证。"""
    text = "| 环节 | 说明 |\n|---|---|\n| 责任能力 | 无异常 |\n"
    result = check_report(load_system("three-tier"), text)
    assert any("责任能力" in m for m in result["missing"])


def test_check_heading_hit_is_strongest_evidence():
    text = "## 违法阻却事由\n\n本案无正当化事由。\n"
    result = check_report(load_system("three-tier"), text)
    detail = next(d for d in result["details"] if d["check"] == "违法阻却事由")
    assert detail["status"] == "标题"
    assert detail["matched_via"] == "违法阻却事由"


def test_check_details_and_formats():
    result = check_report(load_system("three-tier"), CRIMINAL_SAMPLE.read_text(encoding="utf-8"))
    assert result["details"], "details 必须逐项给出匹配证据"
    assert all({"stage", "check", "status"} <= set(d) for d in result["details"])
    md = format_result_md(result)
    assert md.startswith("# 检视校验报告")
    assert "| 阶层 | 必检环节 |" in md
    assert "覆盖率" in format_result(result)
    payload = json.dumps(result, ensure_ascii=False)
    assert '"details"' in payload


def test_crime_forms_covers_attempt_and_omission():
    """犯罪形态程式必须区分未遂与不作为，二者结构与标准三阶层不同。"""
    system = load_system("crime-forms")
    outline = render_outline(system)
    for label in ("未遂犯", "共犯", "不作为犯", "过失犯"):
        assert label in outline


def test_proportionality_declares_three_levels():
    """论证深度三层是比例原则的核心，缺一层即失衡。"""
    system = load_system("proportionality")
    outline = render_outline(system)
    for label in ("第一层", "第二层", "第三层"):
        assert label in outline
    assert "结论一致则不问理由" in outline


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


def test_practice_hides_elements_but_counts_them():
    """练习卷只给检视提示：要素内容必须隐藏，数量提示必须给出。"""
    system = load_system("three-tier")
    text = render_practice(system)
    assert "设问" in text
    assert "实行行为" not in text, "练习卷不得泄露要件要素内容"
    assert "个要件要素" in text
    assert "学术诚信" in text


def test_practice_self_check_comes_from_proportionality_data():
    """自查清单应取自 proportionality 体系的数据，而非写死在代码里。"""
    text = render_practice(load_system("three-tier"))
    assert "成稿自查清单" in text
    assert "涵摄四步法" in text  # proportionality.self_check 的要素之一


def test_practice_html_is_self_contained():
    html = render_practice_html(load_system("claim-basis"))
    assert html.startswith("<!DOCTYPE html>")
    assert 'class="answer"' in html
    assert "http://" not in html


def test_offense_theft_declares_amount_thresholds():
    """盗窃罪程式必须写明数额档位的规范依据。"""
    system = load_system("offense-theft")
    text = render_outline(system)
    assert "法释〔2013〕8 号" in text
    assert "指导案例 27 号" in text


def test_administrative_legality_mirrors_article_70():
    """行政法程式的审查项须与《行政诉讼法》第 70 条的撤销情形对应。"""
    system = load_system("administrative-legality")
    text = render_outline(system)
    assert "第 70 条" in text
    assert "正当程序" in text

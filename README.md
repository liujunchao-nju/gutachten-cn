# gutachten-cn

[![tests](https://github.com/liujunchao-nju/gutachten-cn/actions/workflows/tests.yml/badge.svg)](https://github.com/liujunchao-nju/gutachten-cn/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

把「鉴定式案例分析」的方法论编码成可加载、可渲染、可校验的开源工具。覆盖刑法阶层检验与民法请求权基础两条线。

## 为什么做这个

鉴定式分析（Gutachten）的价值在于**递进式筛查**：前一阶层不成立就不必进入下一阶层，每一处结论都要落到法条与事实的涵摄上。它的难点不在概念，而在**不漏环节**。写一份三阶层分析，最常见的失误是跳过违法性阶层，或者只写客观要件、忘了主观要件；写请求权基础分析，则常常直接从侵权或不当得利下手，跳过契约上请求权。

这个工具把检视程式抽出来，写成可配置的 YAML。你会得到三样东西：一份可勾选的检视大纲、一个能查出漏项的校验器、两篇可对照的公开案例范文。

## 安装

```bash
pip install -e .
```

只依赖 `PyYAML`。Python 3.9 及以上。

## 用法

```bash
# 列出全部检视体系
python -m gutachten_cn list

# 查看某体系的说明与规则依据
python -m gutachten_cn show --system claim-basis

# 生成检视大纲（可带案件信息）
python -m gutachten_cn outline --domain criminal --case examples/case_input.json

# 校验一份报告是否遗漏必检环节
python -m gutachten_cn check --system three-tier --file examples/criminal_sample.md
```

`check` 的逻辑很简单：逐一比对报告正文中是否出现各必检环节的标题，未出现的列为缺失。它只做提醒，不判分，也不要求用词一致。

Python API：

```python
from gutachten_cn import load_system, render_outline, check_report

system = load_system("three-tier")
print(render_outline(system))
print(check_report(system, open("报告.md", encoding="utf-8").read())["missing"])
```

## 支持的检视体系

| 体系 | 领域 | 默认 | 说明 |
|---|---|:---:|---|
| `three-tier` | 刑法 | ✓ | 三阶层：构成要件该当性 → 违法性 → 有责性 |
| `two-tier` | 刑法 | | 二阶层：客观不法层 → 主观责任层（张明楷） |
| `four-element` | 刑法 | | 四要件：客体 / 客观方面 / 主体 / 主观方面（法考结论校验层） |
| `examination-sequence` | 刑法 | | 五步分析法：事实单元划分 → 参与人列举 → 犯罪检验 → 竞合 → 全案结论（宏观框架） |
| `crime-forms` | 刑法 | | 犯罪形态检视程式：未遂 / 共犯 / 不作为 / 过失各有专门程式 |
| `proportionality` | 通用 | | 论证深度比例原则：明显者一句、争议者涵摄、核心争议穷尽方法论 |
| `claim-basis` | 民法 | ✓ | 请求权基础七步检索（王泽鉴） |

** `three-tier` 与 `examination-sequence` 的分工**：前者规定「涉嫌犯罪检验」这一步的内部结构（递进三阶层），后者规定这一步之前与之后的环节（如何切分事实单元、按什么顺序分析参与人、如何处理竞合、结论须含哪些要素）。二者配合使用才是一份完整报告。

### 论证深度：为什么不能平均用力

这是鉴定式写作最容易被忽视、也最见功力的一环。核心命题是**论证深度与争议程度成正比**：

| 层级 | 要素特征 | 论证模式 | 篇幅 |
|---|---|---|---|
| 第一层 | 明显成立或不成立 | 裁判式 | 1–2 句 |
| 第二层 | 存在合理争议 | 标准鉴定式·涵摄四步法 | 1–2 段 |
| 第三层 | 核心争议焦点 | 涵摄 + 法律解释 + 学说争议 + 反对说回应 | 多段或整节 |

优秀的鉴定式报告如同五花肉，肥瘦相间、节奏分明。全肥则冗长无重点，全瘦则单薄无深度，**肥瘦倒置（显然者详写、争议者略写）则本末倒置**。判层级的四问是：核心语义检验、概念可把握性、学说或实务分歧、决定性检验。

配套纪律有两条：「结论一致则不问理由」（各说结论相同时无需展开争议，但应在脚注点明），以及「选择立场须给出积极理由」（不得仅否定其他立场）。

### 关于刑法体系的选择

这里有一个必须说清的事实：**司法部马工程教材（2025 年 5 月明确）载明，法考以四要件为基础，允许运用阶层论的思维方式辅助分析**，即定罪结论应与四要件一致，而分析过程可先判断客观（不法）、再判断主观（责任）。

同时也要承认：**鉴定式分析必须使用阶层体系**。四要件是平面耦合结构，四个要件并列、一次性整体评价，没有递进筛查的逻辑，无法承载「先检验该当性、再检验违法性、最后检验有责性」这种层次推进。

因此本仓库的处理方式是：

- **分析过程**用三阶层（默认），可选二阶层；
- **定罪结论**用 `four-element` 回到四要件核对，与法考口径收敛；
- 两者不冲突，恰好对应官方「过程可分层、结论须一致」的表述。

若你的课程或考试以二阶层为准，把 `three-tier.yaml` 的 `default` 改为 `false`、`two-tier.yaml` 改为 `true` 即可，无需改任何代码。

### 民法请求权基础的检索顺序

核心命题为「**谁得向谁，依据何种法律规范，主张何种权利**」。检索顺序固定为：

1. 契约上请求权
2. 无权代理等类似契约关系上请求权
3. 无因管理上请求权
4. 物权关系上请求权
5. 不当得利请求权
6. 侵权行为损害赔偿请求权
7. 其他请求权

顺序的理由是：契约关系多为其他请求权的前提问题。当事人间有委托合同即不构成无因管理；基于合同占有某物即属有权占有；有合同关系时一方取得的利益具有法律上原因，不构成不当得利。该顺序经五个独立权威来源表述一致（湖北高院、河南新县法院、河北定州法院、北京法院网、中国法院网），并已由测试锁定。

## 设计：方法论即数据

所有检视程式定义在 `gutachten_cn/schemas/*.yaml`，Python 代码里没有任何硬编码的阶层名称或要件清单。

```yaml
- id: schuld
  label: 有责性
  order: 3
  nature: 消极检验
  checks:
    - id: capacity
      label: 责任能力
      required: true
      elements:
        - 刑事责任年龄
        - 辨认能力与控制能力
```

由此带来两个直接好处：**新增一套检视体系不用改代码**，放一个 YAML 文件即可，`list` 命令会自动识别；**改要件不用改代码**，编辑 `elements` 列表即可，大纲与校验随之更新。

每个体系的 `source` 字段都写明了规则依据出处，可用 `show --system <名称>` 查看。

## 规则依据

- 刑法三阶层：当代三阶层犯罪论体系，构成要件符合性同时包含客观与主观构成要件（行为无价值二元论立场）。
- 刑法二阶层：张明楷《刑法学》「以违法与责任为支柱构建犯罪论体系」。
- 四要件与法考口径：司法部马工程教材（2025 年 5 月明确）。
- 民法请求权基础：王泽鉴《民法思维——请求权基础理论体系》。
- 涵摄方法：总起句（设问）→ 定义 → 归入 → 结论。

测试共 24 项，其中两项以本仓库收录的公开案例范文作回归基准：刑法范文须覆盖三阶层全部必检环节，民法范文须覆盖请求权基础全部必检环节；另有两项分别锁定犯罪形态程式的四类名目与论证深度的三层结构。每次 push 与 PR 会由 [GitHub Actions](https://github.com/liujunchao-nju/gutachten-cn/actions/workflows/tests.yml) 在 Python 3.9 / 3.11 / 3.13 上自动复跑。

## 范文

| 文件 | 案件 | 体系 | 教学价值 |
|---|---|---|---|
| `examples/criminal_sample.md` | （2025）沪0117刑初373号，上海市松江区人民法院 | 三阶层 | 同一被告人兼具**既遂与未遂**两个事实单元，可完整展开着手、既未遂区分与入户盗窃加重情节 |
| `examples/civil_sample.md` | （2023）辽1481民初3391号，兴城市人民法院 | 请求权基础七步 | 立案案由原为**不当得利**、庭审变更为**买卖合同**，天然演示「契约上请求权优先、有合同即排除不当得利」 |

两篇范文的事实均取自公开裁判文书，案号齐全可复核，人物名称沿用文书中的匿名化表述。

## 已知限制

1. `check` 采用文本匹配，若报告使用了同义表述（如「违法阻却事由」写作「正当化事由」）会被判为缺失。已做的处理：匹配时**排除 Markdown 表格行**，避免说明性表格（如论证深度一览）中提及的要件名被误判为已展开论证；后续可考虑引入同义词表。
2. 目前只收录了两篇范文，覆盖盗窃罪与买卖合同纠纷。故意犯、过失犯、不作为犯、共犯、错误论、竞合等犯罪形态的检视程式尚未纳入本仓库，仅在配套的 `gutachten-criminal-case` 工作流中以方法论形式存在。
3. 本工具不做法条时效性核验，引用条文前请自行核对现行有效版本。
4. 检视程式的学派立场（行为无价值二元论）写死在 `source` 字段说明中，未做成可切换项。同一份报告内不应混用不同立场。

## 免责声明

本项目是学习方法论与工具实践的产物，不构成法律意见，也不保证输出符合任何课程或考试的具体要求。法条与案例请自行核对；正式提交作业或参加考试前，请按指导教师与最新教材的要求复核。

## English

`gutachten-cn` turns the German-style *Gutachten* method (structured case analysis) into loadable, renderable, checkable tooling for Chinese law. It ships four examination schemas: two criminal-law tier systems plus the four-element check used by China's bar exam, and the seven-step claim-basis search for civil law. Schemas live in YAML, so adding a school of thought is a file, not a refactor. Two sample analyses built on published judgments serve as regression anchors.

## 许可

MIT。见 [LICENSE](LICENSE)。

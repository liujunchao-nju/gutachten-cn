# gutachten-cn

[![tests](https://github.com/liujunchao-nju/gutachten-cn/actions/workflows/tests.yml/badge.svg)](https://github.com/liujunchao-nju/gutachten-cn/actions/workflows/tests.yml)
[![version](https://img.shields.io/badge/version-v0.3.0-blue.svg)](https://github.com/liujunchao-nju/gutachten-cn/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![agent skill](https://img.shields.io/badge/agent-skill-8b0000.svg)](SKILL.md)

[![Star History Chart](https://api.star-history.com/svg?repos=liujunchao-nju/gutachten-cn&type=Date)](https://star-history.com/#liujunchao-nju/gutachten-cn&Date)

把「鉴定式案例分析」的方法论编码成可加载、可渲染、可校验的开源工具。覆盖刑法阶层检验、具体罪名程式、民法请求权基础各论与行政行为合法性审查四条线，共 17 套检视体系。既是一个 Python 包，也是一个可安装的 agent skill。

## 为什么做这个

鉴定式分析（Gutachten）的价值在于**递进式筛查**：前一阶层不成立就不必进入下一阶层，每一处结论都要落到法条与事实的涵摄上。它的难点不在概念，而在**不漏环节**。写一份三阶层分析，最常见的失误是跳过违法性阶层，或者只写客观要件、忘了主观要件；写请求权基础分析，则常常直接从侵权或不当得利下手，跳过契约上请求权。

这个工具把检视程式抽出来，写成可配置的 YAML。你会得到四样东西：一份可勾选的检视大纲、一个能查出漏项的校验器、一份只给提示的练习卷、六篇可对照的公开案例范文。

## 安装

Python 包（只依赖 `PyYAML`，Python 3.9 及以上）：

```bash
pip install -e .
```

作为 agent skill 安装（Claude Code、Codex 等支持本地 skill 的平台）：

```bash
npx skills add https://github.com/liujunchao-nju/gutachten-cn
```

两种形态共享同一套数据与代码：skill 提供触发与使用说明，包提供命令与 API。

## 用法

```bash
# 列出全部检视体系
python -m gutachten_cn list

# 查看某体系的说明与规则依据
python -m gutachten_cn show --system claim-basis

# 生成检视大纲（md 或 html，html 为零依赖单文件，可勾选）
python -m gutachten_cn outline --domain criminal --case examples/case_input.json
python -m gutachten_cn outline --system three-tier --format html --out outline.html

# 生成练习卷：只给设问与要素数量，不给要素内容
python -m gutachten_cn practice --system three-tier --case examples/case_input.json

# 校验一份报告是否遗漏必检环节（text / json / md 三种输出）
python -m gutachten_cn check --system three-tier --file examples/criminal_sample.md
python -m gutachten_cn check --system three-tier --file 报告.md --format md --out check-report.md
```

`check` 的匹配分三级证据：**标题命中**（环节名或其别称出现在 Markdown 标题中，最强证据）、**正文命中**（出现在正文行，排除表格行）、**缺失**。同义表述（如「违法阻却事由」与「正当化事由」）收入各程式 YAML 的 `aliases` 字段，新增同义词不用改代码。它只做提醒，不判分，也不要求用词一致。

Python API：

```python
from gutachten_cn import load_system, render_outline, check_report, render_practice

system = load_system("three-tier")
print(render_outline(system))                      # md 大纲
print(render_outline(system, fmt="html"))          # html 大纲
print(render_practice(system))                     # 练习卷
print(check_report(system, open("报告.md", encoding="utf-8").read())["missing"])
```

## 支持的检视体系（17 套）

### 刑法

| 体系 | 默认 | 说明 |
|---|:---:|---|
| `three-tier` | ✓ | 三阶层：构成要件该当性 → 违法性 → 有责性 |
| `two-tier` | | 二阶层：客观不法层 → 主观责任层（张明楷） |
| `four-element` | | 四要件：客体 / 客观方面 / 主体 / 主观方面（法考结论校验层） |
| `examination-sequence` | | 五步分析法：事实单元划分 → 参与人列举 → 犯罪检验 → 竞合 → 全案结论（宏观框架） |
| `crime-forms` | | 犯罪形态检视程式：未遂 / 共犯 / 不作为 / 过失各有专门程式 |
| `offense-theft` | | 盗窃罪检视程式：平和手段、非法占有目的、数额档位、盗骗区分 |
| `offense-fraud` | | 诈骗罪检视程式：欺骗 → 认识错误 → 处分 → 取得的因果链 |
| `offense-homicide` | | 故意杀人罪检视程式：生命法益、故意内容界分、未完成形态 |
| `offense-misappropriation` | | 侵占罪检视程式：已然占有、拒不退还、与盗窃的界分 |

### 民法

| 体系 | 默认 | 说明 |
|---|:---:|---|
| `claim-basis` | ✓ | 请求权基础七步检索（王泽鉴） |
| `contract-claim` | | 契约上请求权检视程式：成立生效 → 给付义务 → 债务不履行 → 违约责任 |
| `tort-claim` | | 侵权行为损害赔偿请求权检视程式：六要件 → 抗辩减责 → 特殊侵权 → 赔偿范围 |
| `property-claim` | | 物权关系上请求权检视程式：确认、返还、排除妨害、消除危险 |
| `unjust-enrichment` | | 不当得利请求权检视程式：三要件与返还范围 |
| `negotiorum` | | 无因管理上请求权检视程式：三要件与费用偿还 |

### 行政法与通用

| 体系 | 默认 | 说明 |
|---|:---:|---|
| `administrative-legality` | | 行政行为合法性审查：受案范围、职权、证据、法律适用、程序、裁量与比例 |
| `proportionality` | | 论证深度比例原则：明显者一句、争议者涵摄、核心争议穷尽方法论 |

**体系之间的分工**：`examination-sequence` 规定宏观路径，「涉嫌犯罪检验」这一步的内部结构由 `three-tier` 规定；具体罪名进入对应的 `offense-*` 程式；民法在 `claim-basis` 确定成立哪类请求权后，进入对应各论程式深挖；`proportionality` 规定每一处要件的论证篇幅。它们配合使用才是一份完整报告。

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
      aliases: [刑事责任能力]
      elements:
        - 刑事责任年龄
        - 辨认能力与控制能力
```

由此带来三个直接好处：**新增一套检视体系不用改代码**，放一个 YAML 文件即可，`list` 命令会自动识别；**改要件不用改代码**，编辑 `elements` 列表即可，大纲与校验随之更新；**新增同义表述不用改代码**，编辑 `aliases` 即可。

每个体系的 `source` 字段都写明了规则依据出处，可用 `show --system <名称>` 查看。

## 规则依据

- 刑法三阶层：当代三阶层犯罪论体系，构成要件符合性同时包含客观与主观构成要件（行为无价值二元论立场）。
- 刑法二阶层：张明楷《刑法学》「以违法与责任为支柱构建犯罪论体系」。
- 四要件与法考口径：司法部马工程教材（2025 年 5 月明确）。
- 民法请求权基础：王泽鉴《民法思维——请求权基础理论体系》。
- 盗窃罪数额档位：两高《关于办理盗窃刑事案件适用法律若干问题的解释》（法释〔2013〕8 号）。
- 诈骗罪数额档位：两高《关于办理诈骗刑事案件具体应用法律若干问题的解释》（法释〔2011〕7 号）。
- 民法各论：《民法典》合同编、物权编、侵权责任编相应条文。
- 行政行为合法性审查：《行政诉讼法》第 70 条列举的撤销情形。
- 涵摄方法：总起句（设问）→ 定义 → 归入 → 结论。

测试共 59 项，其中六项以本仓库收录的公开案例范文作回归基准（每篇范文须覆盖对应体系的全部必检环节）；每次 push 与 PR 会由 [GitHub Actions](https://github.com/liujunchao-nju/gutachten-cn/actions/workflows/tests.yml) 在 Python 3.9 / 3.11 / 3.13 上自动复跑。

## 范文

| 文件 | 案件 | 体系 | 教学价值 |
|---|---|---|---|
| `examples/criminal_sample.md` | （2025）沪0117刑初373号，上海市松江区人民法院 | 三阶层 | 同一被告人兼具**既遂与未遂**两个事实单元，可完整展开着手、既未遂区分与入户盗窃加重情节 |
| `examples/civil_sample.md` | （2023）辽1481民初3391号，兴城市人民法院 | 请求权基础七步 | 立案案由原为**不当得利**、庭审变更为**买卖合同**，天然演示「契约上请求权优先、有合同即排除不当得利」 |
| `examples/theft_sample.md` | 最高人民法院指导案例 27 号，臧进泉等盗窃、诈骗案 | `offense-theft` | **盗骗区分**的标杆案例：诱骗点击虚假链接而实际由植入程序窃取财物的定盗窃，欺骗处分财产的定诈骗 |
| `examples/tort_sample.md` | 最高人民法院指导案例 24 号，荣宝英诉王阳等交通事故责任纠纷案 | `tort-claim` | 受害人**特殊体质不减轻侵权人责任**：损伤参与度不是法律上的过错，不得据此扣减残疾赔偿金 |
| `examples/contract_sample.md` | 最高人民法院指导案例 23 号，孙银山诉欧尚超市江宁店买卖合同纠纷案 | `contract-claim` | 契约上请求权的完整展开，兼示**食品安全十倍赔偿**与「明知购买不影响请求权成立」 |
| `examples/admin_sample.md` | 最高人民法院指导案例 38 号，田永诉北京科技大学拒绝颁发毕业证、学位证案 | `administrative-legality` | 高校退学处理的合法性审查范本：上位法依据、正当程序（送达与申辩）与比例原则 |

范文事实均取自公开裁判文书或最高人民法院指导性案例，案号齐全可复核，人物名称沿用文书中的匿名化表述。

## 常见问题

**Q：`check` 报缺失，但我确实写了这个环节？**
先看输出里的「命中方式」。正文命中算通过；如果换用了未收录的表述（例如把「期待可能性」写成「他律期待」），会报缺失。此时有两个选择：接受提醒人工确认，或者在该程式 YAML 的 `aliases` 里补上这个说法（欢迎提 PR）。

**Q：为什么刑法默认三阶层，而不是四要件？**
鉴定式依赖递进筛查，四要件是平面耦合结构，没有递进逻辑。官方口径是「过程可分层、结论须一致」，所以本仓库用三阶层分析、用四要件校验结论，两者都提供。

**Q：练习卷为什么不给完整大纲？**
直接给大纲，练习就变成了抄写。练习卷只给设问和「本环节含几个要素」的数量提示，先独立作答再对照 `outline` 自评，才是训练。

**Q：可以拿它写课程作业吗？**
可以用它训练方法、检查结构，但不得将工具产出直接作为本人作业提交（见学术诚信）。作业的具体要求请以指导教师与教材为准。

**Q：法条会过期吗？**
会。本工具不做法条时效性核验，范文与程式中的法条引用请以官方法律数据库的现行版本为准；引用前务必核对。

## 已知限制

1. `check` 采用标题与正文的文本匹配，未收录的同义表述仍会报缺失（已收入常用别称于 `aliases`，并排除表格行与「只在表格里提一句」的误判；后续可引入词向量相似度兜底）。
2. 具体罪名程式目前覆盖盗窃、诈骗、故意杀人、侵占四罪，其余罪名可按同样的 YAML 契约扩充（见 [CONTRIBUTING.md](CONTRIBUTING.md)）。
3. 本工具不做法条时效性核验，引用条文前请自行核对现行有效版本。
4. 检视程式的学派立场（三阶层采行为无价值二元论）写在各体系 `source` 字段说明中，未做成可切换项。同一份报告内不应混用不同立场。

## 学术诚信

本工具是学习方法论与训练思维的工具，不是代写工具。使用者可以将工具产出用于自学、训练与结构自检，但不得将其直接作为本人课程作业、竞赛作品或考试答案提交；正式提交前，请按指导教师与最新教材的要求复核。滥用工具完成学业考核，后果由使用者自行承担。

## 免责声明

本项目是学习方法论与工具实践的产物，不构成法律意见，也不保证输出符合任何课程或考试的具体要求。法条与案例请自行核对。

## 作者

刘俊超，南京大学法学院本科生。关注法律检索、引注规范与法学方法论的工具化。

- GitHub：[liujunchao-nju](https://github.com/liujunchao-nju)
- 邮箱：251820244@smail.nju.edu.cn
- 相关项目：[cn-legal-citation](https://github.com/liujunchao-nju/cn-legal-citation)（《法学引注手册》引注生成）、[contract-review-checklist](https://github.com/liujunchao-nju/contract-review-checklist)（合同审查清单）、[legal-writing-samples](https://github.com/liujunchao-nju/legal-writing-samples)（法律文书范文库）

欢迎通过 Issue 或 Pull Request 贡献检视程式、同义词与范文。

## English

`gutachten-cn` turns the German-style *Gutachten* method (structured case analysis) into loadable, renderable, checkable tooling for Chinese law. Seventeen examination schemas cover the three-tier / two-tier / four-element criminal frameworks, four specific offenses (theft, fraud, homicide, misappropriation), the seven-step claim-basis search plus per-doctrine civil procedures, and administrative legality review. Schemas live in YAML, so adding a school of thought is a file, not a refactor. It ships as both a Python package and an installable agent skill, renders outlines in Markdown or self-contained HTML, offers a Socratic practice mode, and checks reports for missing required steps with a three-tier evidence model (heading / body / missing). Six sample analyses built on published judgments and SPC guiding cases serve as regression anchors.

## 许可

MIT。见 [LICENSE](LICENSE)。

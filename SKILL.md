---
name: gutachten-cn
description: 鉴定式案例分析（Gutachten）检视程式工具。当用户需要按三阶层犯罪论、二阶层体系、四要件（法考口径）分析刑法案例，或按请求权基础方法分析民法案例，或审查行政行为合法性时使用；也可用于生成可勾选的检视大纲、生成只给提示的练习卷、校验案例分析报告是否遗漏必检环节。触发词：鉴定式案例分析、Gutachten、三阶层检验、二阶层、四要件、请求权基础、涵摄、构成要件该当性、违法阻却事由、有责性、犯罪论检视、案例研习报告、盗窃罪、诈骗罪、故意杀人罪、侵占罪、不当得利、无因管理、侵权行为、契约、行政行为合法性审查、检视程式、漏项检查。
version: 0.3.0
---

# gutachten-cn：鉴定式案例分析的检视程式工具

把「鉴定式案例分析」的方法论编码成可加载、可渲染、可校验的开源工具。
检视程式全部定义在 YAML 中（方法论即数据），Python 代码只负责加载、
渲染与校验。覆盖刑法阶层检验、具体罪名程式、民法请求权基础各论、
行政行为合法性审查共 17 套体系。

## 一、什么时候用本 skill

用户需要下面任一帮助时：

- 按三阶层（或二阶层、四要件）分析一个刑法案例，怕漏掉违法性或有责性阶层；
- 按请求权基础方法分析民法案例，怕跳过契约上请求权直接从侵权下手；
- 审查行政行为（行政处罚、退学处理、拒绝颁证等）的合法性；
- 想要一份可勾选的检视大纲，或者一份「只给提示不给答案」的练习卷；
- 写完了鉴定式报告，想用工具查出是否遗漏必检环节。

**不适用**：具体诉讼文书起草（起诉状、辩护词等）请用文书类工具；
法条时效性核验请配合官方法律数据库（本工具不做法条核验，见第六节纪律）。

## 二、安装

```bash
pip install -e .        # 只依赖 PyYAML，Python 3.9+
```

作为 agent skill 安装（Claude Code / Codex 等支持本地 skill 的平台）：

```bash
npx skills add https://github.com/liujunchao-nju/gutachten-cn
```

## 三、五个子命令

| 命令 | 用途 | 何时用 |
|---|---|---|
| `list` | 列出全部检视体系 | 不确定用哪套体系时 |
| `show --system X` | 查看体系的说明、涵摄方法与规则依据 | 选定体系后，先看依据再动手 |
| `outline` | 生成可勾选检视大纲（md 或 html） | 拿到案件材料后，先立骨架再写作 |
| `practice` | 生成练习卷：只给设问与要素数量，不给要素内容 | 训练场景，防止照抄大纲 |
| `check` | 校验报告是否遗漏必检环节，输出覆盖率 | 成稿后自查 |

```bash
python -m gutachten_cn list
python -m gutachten_cn show --system three-tier
python -m gutachten_cn outline --system three-tier --case case.json --format html --out outline.html
python -m gutachten_cn practice --system claim-basis --case case.json
python -m gutachten_cn check --system three-tier --file report.md --format md --out check-report.md
```

## 四、典型工作流

```
拿到案件材料
  │
  ▼
list / show：确定检视体系（ criminal → three-tier 或具体罪名程式；
 civil → claim-basis 起步，成立某项后进入对应各论程式；
 administrative → administrative-legality ）
  │
  ▼
outline：生成检视大纲（带案件信息时传 --case case.json）
  │
  ▼
按大纲逐层写作（涵摄四步法：总起句 → 定义 → 归入 → 结论）
  │
  ▼
check：校验必检环节覆盖率，缺失项逐项补写
```

**体系配合关系**：`examination-sequence`（五步分析法）规定宏观路径，
`three-tier` 规定第三步「涉嫌犯罪检验」的内部结构，`crime-forms` 规定
未遂、共犯、不作为、过失的变体程式，`proportionality` 规定论证深度。
写一份完整报告通常需要它们配合，而非只用一套。

## 五、输出与纪律

1. **学派立场显式化**：三阶层体系采行为无价值二元论立场，二阶层采张明楷
   《刑法学》立场。同一份报告内不得混用不同立场；切换体系改 YAML 的
   `default` 字段即可，不需要改代码。
2. **法条时效自行核验**：本工具不做法条时效性核验，引用条文前请对照
   官方法律数据库核对现行有效版本；范文中的法条已尽量标注现行对应条文。
3. **案号真实可复核**：范文均取自公开裁判文书或者最高人民法院指导性
   案例，案号齐全；不得虚构案号。
4. **学术诚信**：`practice` 生成的练习卷用于方法论训练，使用者应先独立
   完成作答再对照大纲自评，不得将工具产出直接作为本人课程作业或者
   考试答案提交。
5. **check 的定位是提醒不是判分**：缺失仅表示报告中找不到对应环节，
   可能是遗漏，也可能是换用了未收录的同义表述（同义表述已尽量收入
   YAML 的 `aliases` 字段）。

## 六、降级说明

- 环境无 PyYAML：无法加载检视程式，本 skill 不可用（无纯标准库兜底路径，
  这是有意的取舍：方法论数据的完整性优先）。
- 报告的 Markdown 结构混乱（无标题、无层级）：`check` 退化为正文文本
  匹配，覆盖率仍可参考，但标题命中数会偏低。
- 案件材料为 PDF/图片：先自行转成 Markdown 再进入工作流，本工具不提供
  文档解析。

## 七、目录结构

```
gutachten-cn/
├── SKILL.md                     # 本文件
├── README.md                    # 项目主页
├── gutachten_cn/
│   ├── schemas/                 # 全部检视程式（方法论即数据）
│   │   ├── criminal/            # 三阶层、二阶层、四要件、五步分析法、犯罪形态、罪名程式
│   │   ├── civil/               # 请求权基础七步 + 契约、侵权、物权、不当得利、无因管理
│   │   ├── administrative/      # 行政行为合法性审查
│   │   └── shared/              # 论证深度比例原则
│   ├── check.py                 # 漏项校验（标题/正文/缺失三级证据 + 同义词）
│   ├── render.py                # 大纲渲染（md / html）
│   ├── practice.py              # 练习卷渲染
│   └── cli.py                   # 命令行入口
├── examples/                    # 六篇公开案例范文（回归基准）
└── tests/                       # 测试（范文覆盖率锚定）
```

## 八、配套 skill

写作全流程（案情解析 → 罪名发现 → 预选确认 → 大纲确认 → 并行写作 →
三维核验 → Word 输出）由配套工作流 `gutachten-criminal-case` 负责；
本 skill 提供其中的检视程式数据层与校验能力。两者是引擎与工作流的关系。

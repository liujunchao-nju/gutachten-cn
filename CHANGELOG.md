# 更新日志

本项目的版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [0.3.0] - 2026-10-15

主题：**Skill 化 + 校验器升级 + 体系扩充**。

### 新增

- **Agent Skill 形态**：新增根目录 `SKILL.md`（含触发词工程），可通过
  `npx skills add https://github.com/liujunchao-nju/gutachten-cn` 一键安装。
- **check 校验器升级**：匹配改为三级证据（标题命中 / 正文命中 / 缺失），
  新增 `--format json|md` 输出与 `details` 逐项证据明细；同义表述改由各
  程式 YAML 的 `aliases` 字段驱动，新增同义词不再需要改代码。
- **outline 新增 HTML 导出**：`--format html` 产出零依赖单文件（内联 CSS
  与 JS），带勾选进度条，离线可开。
- **practice 练习模式**：新子命令生成「只给设问与要素数量、不给要素内容」
  的练习卷（md / html），自查清单取自 proportionality 体系数据，附学术
  诚信声明。
- **十套新检视程式**：
  - 刑法：`offense-theft`（盗窃）、`offense-fraud`（诈骗）、
    `offense-homicide`（故意杀人）、`offense-misappropriation`（侵占）；
  - 民法：`contract-claim`（契约）、`tort-claim`（侵权）、
    `property-claim`（物权）、`unjust-enrichment`（不当得利）、
    `negotiorum`（无因管理）；
  - 行政法：`administrative-legality`（行政行为合法性审查）。
- **四篇新范文**（均为公开可核验案例）：指导案例 27 号（臧进泉等盗窃、
  诈骗案）、指导案例 24 号（荣宝英案）、指导案例 23 号（孙银山案）、
  指导案例 38 号（田永案），分别锚定对应新程式。
- 文档工程：README 增加版本徽章、Star History、FAQ、作者卡片；
  新增 `CHANGELOG.md` 与 `CONTRIBUTING.md`。

### 变更

- 版本号 0.1.0 → 0.3.0（`pyproject.toml` 与 `gutachten_cn.__version__`）。
- `check_report` 返回 dict 新增 `details` 键；既有键
  （`found` / `missing` / `coverage` / `complete`）含义不变。
- 七套既有程式补录 `aliases` 同义词。

### 测试

- 24 项 → 59 项；新增别名命中、表格行排除、标题证据、HTML 自包含、
  练习卷不泄露要素、四篇新范文覆盖率锚定等测试。

## [0.2.0] - 2026-10-14

- 新增三套检视程式：`examination-sequence`（五步分析法）、
  `crime-forms`（犯罪形态）、`proportionality`（论证深度比例原则）。
- 优化两篇范文的事实单元划分与论证深度分层。

## [0.1.0] - 2026-10-14

- 首个版本：三阶层 / 二阶层 / 四要件 / 请求权基础七步四套程式。
- CLI 四子命令（list / show / outline / check），两篇公开案例范文，
  24 项测试，GitHub Actions 多版本 CI。

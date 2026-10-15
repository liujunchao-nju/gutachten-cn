# 贡献指南

欢迎贡献检视程式、同义词、范文与文档。本仓库的核心纪律只有一条：
**方法论即数据，且数据必须有依据**。

## 环境准备

```bash
git clone git@github.com:liujunchao-nju/gutachten-cn.git
cd gutachten-cn
pip install -e ".[dev]"
python -m pytest -q        # 提交前必须全绿
```

## 新增一套检视程式

在 `gutachten_cn/schemas/<domain>/` 下放一个 YAML 文件即可，`list` 会自动识别，不需要改任何代码。文件必须满足以下契约：

```yaml
system: my-system            # 唯一标识，kebab-case
label: 体系中文名
domain: criminal             # criminal / civil / administrative / shared
default: false               # 每域至多一个 true
version: 1
description: >                # 一句话说明这套程式解决什么问题
  ...
source: |                     # 规则依据：必填，且必须真实可查
  《xxx》第 x 条；...
stages:                       # 非空列表，按 order 排序
  - id: stage_id
    label: 阶层名
    order: 1
    nature: 积极检验          # 可选：该阶层的检验性质
    checks:
      - id: check_id
        label: 检验项名
        required: true        # 是否必检（check 只校验 required: true 的项）
        aliases: [同义表述一]  # 可选：同义词，用于 check 匹配
        elements:             # 要件要素列表
          - ...
```

验收标准：

1. **source 必须真实**：写明法规名称、条文号或著作名，不写「通说」这类
   无法核验的出处；引用司法解释写明发布机关与文号。
2. **required 要克制**：真正不可省略的环节才标 `required: true`，选检项
   留给具体案情判断。
3. **跑测试**：`python -m pytest -q` 后，在 `tests/test_gutachten.py` 的
   `EXPECTED_SYSTEMS` 中加入新体系名。

## 补充同义词

发现 `check` 把某种正当表述误判为缺失时，在对应程式该检验项的
`aliases` 里补上这个说法（保持 kebab 风格的简洁中文词），并附一个测试：

```python
def test_check_matches_declared_alias():
    ...
```

## 新增范文

范文是回归基准，纪律最严：

1. **案号必须真实**：取自公开裁判文书或最高人民法院指导性案例，案号
   齐全。不接受虚构、拼接或记不准的案号；无法核实案号的案例不要写。
2. **事实取自公开文本**：按文书或指导案例公布文本摘录，不添加原文没有
   的情节；匿名化表述沿用文书。
3. **覆盖全部必检环节**：范文须通过
   `python -m gutachten_cn check --system <体系> --file <范文>` 的
   100% 覆盖检查，并在 `tests/test_gutachten.py` 的 `SAMPLE_TARGETS`
   登记。
4. **法条标注现行对应**：案例发布时援引的旧法条文，注明现行对应条文
   （如《侵权责任法》第 26 条对应《民法典》第 1173 条）。

## 提交 PR 前的自检

- [ ] `python -m pytest -q` 全绿；
- [ ] README 中出现的每条命令都实跑过；
- [ ] 新增体系已在 README 体系表登记；
- [ ] 新增范文已在 README 范文表与测试登记；
- [ ] 不包含任何虚构的案号、法条或出处。

## 行为边界

- 不提交个人隐私信息、客户材料、商业数据库凭证。
- 不将工具产出包装成法律意见；本项目不提供法律意见。
- 引用指导性案例时，注明批次与发布信息。

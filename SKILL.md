---
name: contract-review
description: AI合同智能审查助手。上传或粘贴合同文本，自动进行9维雷达评分、风险热力图可视化、条款对比修改建议、法律依据引用、谈判策略生成、关键信息提取、合同摘要、时间线可视化、条款结构化解析，输出交互式HTML审查报告。覆盖买卖合同/劳动用工/租赁合同/服务合同/保密协议/投资协议/建设工程/技术开发8类合同类型。触发词：合同审查, 审合同, 合同风险, 合同分析, 审查合同, contract review, 帮我看看合同, 合同审核, 法律风险分析。
version: "2.0.0"
agent_created: true
location: user
allowed-tools: [Read, Write, Edit, Bash, WebSearch, WebFetch, Grep, Glob]
metadata:
  openclaw:
    requires:
      bins:
        - python.exe
    emoji: "📋"
    homepage: https://github.com/bettermen/contract-review
---

# 合同审查 (Contract Review) v2.0

AI驱动的合同智能审查技能，输出交互式可视化HTML审查报告。

## 核心特色

与市面上SaaS合同审查工具不同，本技能提供：
1. **9维雷达评分** — 主体资格/条款完整性/违约责任/争议解决/法律合规/权利义务对等/履约可行性/知识产权/格式规范，按标准化评分算法量化
2. **风险热力图** — 按合同章节可视化风险密度
3. **条款对比修改** — 原文 vs 修改建议并列对比，可直接复制使用
4. **法律依据引用** — 每个风险点引用《民法典》等具体法条
5. **谈判策略生成** — 不止发现问题，提供谈判话术和博弈角度
6. **关键信息提取** — 自动提取主体/金额/日期/付款方式/义务/违约/争议解决/保密条款等结构化信息
7. **合同摘要生成** — 一键生成合同核心内容概述
8. **时间线可视化** — 提取关键日期节点，生成履约时间线
9. **条款结构化解析** — 自动拆分条款树，支持快速导航
10. **完全本地免费** — 无需订阅，离线可用

## 触发条件

当用户提到以下关键词时触发：
- 合同审查、审合同、合同风险、合同分析、审查合同、contract review
- 帮我看看合同、合同审核、法律风险分析
- 用户上传或粘贴合同文本

## 工作流程

### 阶段1：接收合同

1. 确定合同获取方式：文本粘贴 / 文件上传(.txt/.docx/.pdf) / URL
2. 如果是 .docx 或 .pdf 文件，使用 `scripts/parse_contract.py` 提取文本内容
   ```bash
   python scripts/parse_contract.py <file_path> --identify
   ```
3. 如果用户未指定合同类型，根据合同内容自动识别

### 阶段2：关键信息提取

使用 `scripts/extract_key_info.py` 提取结构化关键信息：
```bash
python scripts/extract_key_info.py <file_path> --output key_info.json
# 或直接传入文本
python scripts/extract_key_info.py --text "合同文本..." --output key_info.json
```

提取的信息包括：
- 合同名称
- 签约主体（名称/信用代码/法定代表人）
- 金额信息（总价/单价/定金/保证金/租金等）
- 关键日期（签订日期/合同期限/交付时间等）
- 付款条款（付款方式/发票类型等）
- 权利义务概要
- 违约责任条款
- 争议解决方式
- 保密条款
- 条款结构化列表
- 合同摘要

读取输出的JSON，作为后续审查和报告生成的基础数据。

### 阶段3：合同类型识别与审查清单加载

识别合同类型，加载对应的审查清单：
- 买卖合同 (sales) → 参考 `references/checklist_sales.md`
- 劳动用工合同 (labor) → 参考 `references/checklist_labor.md`
- 租赁合同 (lease) → 参考 `references/checklist_lease.md`
- 服务合同 (service) → 参考 `references/checklist_service.md`
- 保密协议 (nda) → 参考 `references/checklist_nda.md`
- 投资协议 (investment) → 参考 `references/checklist_investment.md`
- 建设工程合同 (construction) → 参考 `references/checklist_construction.md`
- 技术开发合同 (tech_dev) → 参考 `references/checklist_tech_dev.md`

通用审查维度始终生效，参考 `references/checklist_general.md`

### 阶段4：逐维审查与评分

参考 `references/risk_scoring.md` 中的标准化评分方法论，按9个维度逐一审查合同并打分：

**维度1：主体资格 (权重15%)**
- 签约主体合法性（营业执照/授权委托）
- 履约能力评估
- 印章与签字效力

**维度2：条款完整性 (权重15%)**
- 必备条款是否齐全（标的/数量/质量/价款/履行期限/地点/方式/违约责任/争议解决）
- 关键定义是否清晰

**维度3：违约责任 (权重12%)**
- 违约金设定是否合理（不超过损失30%，依据民法典585条）
- 违约情形是否覆盖全面
- 免责条款是否合法

**维度4：争议解决 (权重10%)**
- 管辖法院/仲裁机构是否明确
- 是否违反专属管辖
- 仲裁条款有效性

**维度5：法律合规 (权重15%)**
- 是否违反强制性法律规定
- 格式条款是否公平
- 知识产权归属是否明确

**维度6：权利义务对等性 (权重10%)**
- 双方权利义务是否失衡
- 是否存在霸王条款
- 单方解除权是否合理

**维度7：履约可行性 (权重10%)**
- 交付标准/验收条件是否可执行
- 付款节点是否合理
- 质量标准的可操作性

**维度8：知识产权保护 (权重8%)**
- 知识产权归属约定
- 保密条款完整性
- 竞业限制合理性

**维度9：格式规范性 (权重5%)**
- 结构层次逻辑性
- 语言表述精确度
- 附件与正文协同性

每个维度基准分100分，按评分方法论中的扣分规则扣分。综合评分按各维度权重加权计算。

### 阶段5：风险分级

对发现的风险进行三级分类（参考 `references/risk_scoring.md` 中的致命风险触发条件）：
- 🔴 **致命风险** — 可能导致合同无效、重大损失（如主体无资质、违法条款）
- 🟡 **重大风险** — 可能导致严重不利后果（如违约金过高、管辖不利）
- 🟢 **一般风险** — 可协商改进的瑕疵（如表述模糊、格式不规范）

### 阶段6：生成条款修改建议

对每个风险点：
1. 引用原文条款
2. 提供修改后条款（可直接复制使用）
3. 说明修改理由
4. 引用法律依据（民法典具体条款）
5. 标注所属审查维度

### 阶段7：谈判策略生成

对乙方/弱势方合同：
- 识别谈判优先级（哪些必须改、哪些可让步）
- 提供谈判话术建议
- 分析对方可能反应及应对策略

### 阶段8：生成时间线

从关键信息提取结果中，将关键日期组织为时间线：
- 签订日期 → 交付/开工日期 → 验收日期 → 付款节点 → 合同到期日
- 标注每个节点的履约义务和注意事项

### 阶段9：生成HTML报告

基于 `assets/report_template.html` 模板，将审查结果填入并生成交互式可视化报告。

报告包含模块：
1. 合同摘要卡片（自动生成的核心内容概述）
2. 合同概览卡片（类型/签约方/审查时间/综合评分）
3. 关键信息提取区（结构化展示主体/金额/日期/争议解决等）
4. 9维雷达图（Chart.js，含行业基准对比）
5. 分维度评分明细表（含权重列）
6. 风险热力图（按章节分布）
7. 风险清单表（分级/描述/原文/建议/法律依据/所属维度）
8. 条款对比区（原文 vs 修改建议）
9. Tab切换区：
   - 关键时间线（履约节点可视化）
   - 条款结构（条款树导航）
   - 谈判策略建议
   - 引用法律依据
10. 综合评分卡（A+ ~ F）

**模板使用方法：**
- 读取模板全文
- 将以下占位符替换为实际审查结果JSON：
  - `{{CONTRACT_INFO}}` — 合同基本信息JSON
  - `{{RADAR_DATA}}` — 9维评分数据JSON（每个维度0-100分，含labels/scores/benchmark）
  - `{{RISK_ITEMS}}` — 风险条目数组JSON（每项含level/title/description/original/suggestion/law_ref/dimension）
  - `{{COMPARISON_ITEMS}}` — 条款对比数组JSON（每项含title/clause_ref/original/suggested/reason）
  - `{{NEGOTIATION_STRATEGY}}` — 谈判策略JSON（含overview和items数组）
  - `{{SCORE_CARD}}` — 综合评分数据JSON（含overall_score和overall_grade）
  - `{{LAW_REFERENCES}}` — 法律依据引用数组JSON（每项含law/article/content）
  - `{{HEATMAP_DATA}}` — 热力图数据JSON（含sections和data数组）
  - `{{KEY_INFO}}` — 关键信息提取JSON（来自extract_key_info.py输出）
  - `{{TIMELINE_DATA}}` — 时间线数据JSON（数组，每项含date/title/description）
  - `{{CLAUSE_TREE}}` — 条款结构JSON（数组，每项含number/title/content）
- 将替换后的完整HTML写入工作目录 `contract-review-report.html`

### 阶段10：交付报告

1. 将生成的HTML保存到工作目录
2. 使用 present_files 展示报告
3. 提供简要口头总结，包括：
   - 综合评分与评级
   - 致命风险数量与核心问题
   - 最关键的3条修改建议
   - 谈判优先级排序

## 参考文件

- `references/checklist_general.md` — 通用审查清单（所有合同类型适用）
- `references/checklist_sales.md` — 买卖合同审查清单
- `references/checklist_labor.md` — 劳动用工合同审查清单
- `references/checklist_lease.md` — 租赁合同审查清单
- `references/checklist_service.md` — 服务合同审查清单
- `references/checklist_nda.md` — 保密协议审查清单
- `references/checklist_investment.md` — 投资协议审查清单
- `references/checklist_construction.md` — 建设工程合同审查清单
- `references/checklist_tech_dev.md` — 技术开发合同审查清单
- `references/law_reference.md` — 法律条款引用库
- `references/risk_scoring.md` — 风险评分方法论（标准化评分算法）

## 脚本工具

- `scripts/parse_contract.py` — 合同文本解析（支持docx/pdf/txt，自动识别合同类型）
- `scripts/extract_key_info.py` — 关键信息提取（结构化提取主体/金额/日期/条款等）

## 注意事项

1. 本技能输出的是AI辅助审查建议，不构成法律意见
2. 重大合同建议由专业律师最终审核
3. 审查结果仅供参考，使用者需自行判断
4. 对法律条文的引用可能不完整，重要决策请核实最新法律
5. 关键信息提取基于正则匹配，复杂格式合同可能需要人工校正
6. 评分算法参考 `references/risk_scoring.md`，可根据实际需求调整权重

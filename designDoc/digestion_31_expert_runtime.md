---
title: Expert Runtime Scaffold
status: active_draft
reader_persona:
  - Digestion Orchestrator
  - Digestion Worker Designer
  - Skill Projection Author
---

# Expert Runtime Scaffold

## 1. Purpose

定义 expert 在运行时如何被调用：prompt 怎么组成、expert 之间怎么隔离、shared execution rules 是什么、source 怎么 route 到 expert、多个 expert 怎么并行执行、跨 expert 的信息怎么传递。

本 doc 的读者是 **Orchestrator 和 skill 作者**——需要知道"给 expert 喂什么、怎么喂、产出放哪里"。

Expert 的生命周期（怎么创建、审核、退出）由 [`digestion_30_expert_factory.md`](digestion_30_expert_factory.md) 管理。
Expert 的类型系统（umbrella、source class、routing matrix）由 [`digestion_35_claim_taxonomy_and_source_authority.md`](digestion_35_claim_taxonomy_and_source_authority.md) 管理。
Expert 的产出格式（card、claim schema）由 [`digestion_10_structure_contract.md`](digestion_10_structure_contract.md) 管理。

本 doc 不重复这些定义，只定义它们在 runtime 中如何组装。

## 2. Prompt 组成

当 Orchestrator 向 expert 分发 source 时，构造一个三层 prompt：

| Layer | 内容 | 来源 | 变化频率 |
|-------|------|------|----------|
| General Scaffold | card format、claim schema、permission levels、共享执行规则 | Structure Contract (10) + Claim Taxonomy (35) + 本 doc §4 | 极低（年级别） |
| Expert Design Doc | value chain、channels（含 observables / falsifiers / typical misuse）、source classes（含 allowed / blocked 及原因）、firewall supplements、validation gates、dogfood examples、cross-expert edge 规则 | `designDoc/digestion_5x_*.md`（per expert） | 低（expert 成熟后稳定） |
| Source Material | 原始文本 + 已知 metadata（source_class, observed_at, source_id） | ingestion output | 每次不同 |

每次 invocation 只换中间层。General scaffold 是共享模板；source material 是输入数据。

### 为什么 Layer 2 是 Design Doc 而不是 expert_contract.yaml

Design Doc as Truth 原则定义在 [`digestion_30_expert_factory.md`](digestion_30_expert_factory.md) §7。核心：design doc 是 expert 的完整知识（source of truth），expert_contract.yaml 是派生的 routing/validation index。

Design doc 包含 AI expert 正确判断所需的全部上下文——value chain、typical misuse、validation gates、dogfood examples。这些内容不在 YAML contract 中。因此 prompt 注入 design doc，不注入 YAML contract。

`expert_contract.yaml` 不进 prompt。它服务于 Router（确定性 routing）和 Validator（产出合规检查）。

## 3. Isolation Rule

**一个 expert 一个 prompt invocation。** 不得将多个 expert contract 组合到同一个 prompt 中。

原因：firewall 完整性要求 expert 只看到自己的 subtypes、channels 和 firewall supplements。如果 healthcare_expert 和 ai_semiconductor_expert 共享 context，model 会 blur boundaries——用半导体 subtype 标注 pharma 信号，或反过来。

Expert identity = prompt identity。Domain knowledge 在它是唯一 analytical lens 时激活得最好。

## 4. Shared Execution Rules

所有 expert 共享以下规则，不因 domain 而异：

1. **Card format**: 两层 source card（resource card + angle cards），格式遵循 Structure Contract（digestion_10）
2. **Claim schema**: 所有 claims 必须包含 `claim_type_taxonomy.yaml` → `claim_required_fields` 定义的字段
3. **Permission ceiling**: `permission_level` 不得超过 source 的 `source_class` 所定义的 `permission_level_cap`
4. **Confidence**: ordinal only（low / medium / high），不得使用 cardinal percentages
5. **Falsifiers**: 每条 claim 最少 1 条 falsifier
6. **"What It Does Not Write"**: 每张 angle card 必须包含此 section，显式列出 source 未提供的信息
7. **Reasoning chain**: 每张 angle card 必须包含 `chain_type` + `steps`（observed / implies / preserves 结构）
8. **Use In Synthesis**: 每张 angle card 必须声明 `allowed_as` 和 `disallowed_as`

## 5. Routing Protocol

Expert invocation 之前，routing 步骤决定哪些 experts 消费该 source。

**确定性优先**：用 `source_class`、keywords、tickers 匹配每个 expert 的 `domain`、`source_classes`、`ticker_coverage` 字段（来自 `expert_contract.yaml`）。覆盖约 90% 的 routing 场景。

**AI 补足**：仅在确定性 routing 无法判定时（e.g. 跨行业宏观文章），用 AI semantic routing——以所有 expert descriptions 为 context。

Router input:

```yaml
source_metadata:
  source_class: <source class>
  observed_at: <date>
  tickers_mentioned: []
  keywords: []
expert_registry_ref: claim_type_taxonomy.yaml → expert_registry
```

Router output:

```yaml
relevant_experts: [expert_id_1, expert_id_2]
routing_method: deterministic | ai_supplemented
routing_reason: <one-line explanation>
```

每个 expert 收到独立 invocation。

## 6. Multi-Expert Execution

当一个 source route 到多个 experts 时：

1. **并行 dispatch**：每个 expert 作为独立 prompt invocation 运行（e.g. 独立 Agent calls）。invocation 之间无依赖。
2. **独立产出**：每个 expert 在自己的 subsystem 目录产出 source cards：`data/digestion/expert_subsystems/<expert_id>/source_cards/<source_card_id>/`
3. **无交叉污染**：Expert A 在 digestion 过程中不得读取 Expert B 的产出。每个 expert 只从原始 source material 工作。

## 7. Cross-Expert Edge Protocol

独立 expert invocations 完成后，可通过轻量后处理标注跨 expert edge：

```yaml
cross_expert_edge:
  from_expert: ai_semiconductor_expert
  from_claim_id: sc_10_003
  to_expert: healthcare_expert
  to_claim_id: hc_10_001
  relationship: "51 的 model capability claim 可以 inform 52 的 ai_rd_integration 评估"
  direction: informational
```

规则：

- Edge 是 informational，不是 authority。Expert A 的 claim 不 override Expert B 的 judgment。
- 接收方 expert 在自己的 domain context 中独立评估 informing claim 的含义。
- Edge 标注是可选的；absence of edges 不 invalidate 任何 expert 的产出。

## 8. Detection Boundaries

Runtime-specific violations：

- 一个 source 被 dispatch 到多个 experts 在同一个 shared prompt 中（isolation violation, §3）；
- expert 的 output 引用了另一个 expert 的 subtypes；
- router 在确定性字段可以解决时使用 AI semantic routing（R05 violation）；
- cross-expert edge 被当作 authority override 而非 informational input。

出现以上情况时，停止 downstream promotion，修复调用方式。

## 9. Skill Projection

Skill projection 是 thin wiring layer——不存 domain content，只存组装指令。

每个 expert 的 skill projection 包含：

```yaml
expert_id: healthcare_expert
prompt_layers:
  general_scaffold: designDoc/digestion_31_expert_runtime.md
  expert_knowledge: designDoc/digestion_52_healthcare_expert.md
  contract_for_routing: data/digestion/expert_subsystems/healthcare_expert/expert_contract.yaml
output_root: data/digestion/expert_subsystems/healthcare_expert/source_cards/
```

添加新 expert 的完整路径：

1. 写 design doc（`designDoc/digestion_5x_*.md`）——expert 的完整知识
2. 派生 expert_contract.yaml——machine-readable routing/validation index
3. 在 `claim_type_taxonomy.yaml` → `expert_registry` 注册
4. 加一条 skill projection wiring entry

不需要第三个 truth surface。Design doc 改了，prompt 自然更新；YAML contract 改了，routing 自然更新。Skill projection 只是把两者连接到 runtime scaffold。

## 10. Adjacent Docs

| Doc | Relationship |
|-----|-------------|
| [`digestion_30_expert_factory.md`](digestion_30_expert_factory.md) | Factory 管 expert 的设计和生命周期；本 doc 管 expert 的运行时调用 |
| [`digestion_10_structure_contract.md`](digestion_10_structure_contract.md) | 定义 card 和 claim 的产出格式（General Scaffold Layer 1 的内容来源） |
| [`digestion_35_claim_taxonomy_and_source_authority.md`](digestion_35_claim_taxonomy_and_source_authority.md) | 定义 umbrella types、source classes、routing matrix（General Scaffold Layer 1 的内容来源） |
| `claim_type_taxonomy.yaml` → `expert_registry` | Router 的 expert 列表来源 |

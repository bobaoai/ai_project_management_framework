---
title: 时间戳语义合同（Timestamp Semantic Contract）
layer: T0
t0_layer_id: the_timestamp_semantic
canonical_owner: designDoc/the_timestamp_semantic.md
owned_system_object: time-bearing data semantics
---

# 时间戳语义合同（Timestamp Semantic Contract）

Timestamp Semantics 定义时间字段表示什么、怎样存储、由哪个时钟提供，以及何时可以比较。相同的 UTC 表示不会使来源时间、本地提交时间和运行历史成为同一种时间。本合同规定各系统共同遵守的语义，具体字段登记和验证由代码实现。

## 1. Intended Outcomes

领域设计者、schema 负责人和 Runtime 维护者应能按一致含义定义、存储和比较时间，并取得对应验证依据。

1. **字段用途和来源精度明确。** 时间字段使用既定 role 与兼容 storage，能区分观察、区间、适用、到期、提交、更新、内容有效日期和计划执行。字段不重复对象身份，不从裸名猜测含义，也不补造来源未提供的 instant 精度。
2. **记录时间有正确权威。** 每个持久化记录的提交时间由权威存储分配；未独立持久化的嵌入值不制造第二个提交身份。不可变事实通过追加表达，可变投影保持来源链。外部观察、provider 时间、基础设施历史、进程 wall clock 与 monotonic duration 各有用途，不互相冒充。跨权威 ledger 的排序在可用时使用不可变因果引用、单调版本或 high-water mark；wall-clock 时间和相同 UTC 表示都不能替代因果顺序。
3. **比较结果有完整语义依据。** Role、storage、calendar、转换和 clock relationship 满足相应条件；跨边界判断使用已登记的 converter 或 predicate。默认有效区间遵守半开规则，显式例外有登记依据。条件不满足时返回 typed error，不静默降级为 boolean、UNKNOWN 或 fallback。
4. **时区与日历不会扭曲时间意图。** Local civil time 使用 IANA 时区，交易日由所属日历解析；夏令时歧义按明确 policy 消解并保留决定，或拒绝输入。Physical-hour、business day 和 session 使用各自正确的计量依据，不用固定 offset、固定天数或局部惯例替代。
5. **受保护的跨时钟决定保持保守有效。** Operation 使用固定、不可变的 clock profile 及新鲜、不可变的 health evidence，并按实际 measured bound 执行安全窗口。缺少、过期、不健康、回退、不匹配或不可验证时 fail closed。因果顺序、时钟健康、当前权限和 writer fencing 分别有依据。保守窗口豁免仅适用于 Product Authorization owner 已准入、不再作跨时钟 instant assertion 的 online protocol，且 predicate registration 明确记录、产品合同规定替代 evidence 与 fail-closed 结果。Caller、adapter 和 Module 均无权自行声称例外；只要仍比较跨时钟 instant，profile、evidence 和窗口义务全部保留。
6. **字段准入和当前覆盖可以核对。** Concrete persisted class 有精确登记及 REQ、OPT、FORBIDDEN 要求；未知 class、未经授权字段和 wildcard 不被准入。旧字段只在准确兼容登记下继续有效。登记、predicate、converter、calendar、profile 与覆盖由代码和生成视图提供，手工表格不取得权威。
7. **语义修改与实现工作各有明确归属。** 普通登记变更、稳定语义修改和宪制修改按实际影响选择路径。下层保留领域阈值、调度、生命周期与实现决定；尚待确定的配套设计和实现差异如实交出，不以文稿通过替代 owner 决定或软件采用。

## 2. Owned System Object

本合同管理的对象是 `time-bearing data semantics`。Timestamp Semantics 统一决定：

| 共同定义 | 决定范围 |
| --- | --- |
| Semantic role | 时间角色词汇、含义及互斥边界。 |
| Storage form | 时间点、日历日和市场交易日的表示，以及它们与 role 的兼容条件。 |
| Clock domain | 权威存储、外部 Source、worker、provider、durable backend 和 monotonic clock 各自能提供什么时间依据。 |
| Comparison | 同角色、跨角色、跨日历、跨时钟的比较条件及类型化转换要求。 |
| Timezone 与 DST | IANA 时区、日历和夏令时歧义的处理要求。 |
| Distributed clock safety | 受保护的跨时钟决定所需配置、证据、保守有效窗口和拒绝条件。 |
| Per-class registration | 每个 class 精确登记时间角色，并由代码提供登记事实与生成视图的要求。 |

具体 class、predicate、converter、calendar、clock profile、登记状态和 validator 实现由所属代码持有。领域负责人可以在本合同范围内定义自己的 class、日历、predicate、阈值和工作流程，保持上述共同含义不变。

领域新鲜度阈值、对象生命周期、调度时区与频率、cron expression、市场时间锚点、交易日历 helper 和行情刷新行为由所属领域或调度设计决定。Runtime retry policy、Product permission、非时间 schema、具体实现和迁移历史由各自负责人维护。Timestamp Semantics 提供这些工作使用的时间规则，不执行领域工作，也不编写或追踪 `SystemChangePlan`。

本合同适用于具有时间字段的 schema、API、event、Artifact、decision 和 Runtime record，包括领域新鲜度、调度、授权和执行围栏所使用的时间。具体 validator interface、稳定错误码及调用方动作由代码合同定义；本文不建立额外的公共操作接口。

## 3. System-wide Invariants

本章及后续主题保留 `Timestamp §1` 至 `Timestamp §8`，以及 `Timestamp §6.7` 的逻辑锚点，供已有 code comment、test 和相邻合同引用。

### Timestamp §1 · 双轴字段模型

```text
time-bearing field
    含义：组合一个 semantic role 与一种 storage form 的时间字段。
    命名：semantic role token 与 storage suffix 组合。
    去重：suffix 已含相同 instant 或 date 含义时，移除 role 末尾的 _at 或 _date。
    对象身份：由包含该字段的对象提供，字段名不重复 object name。
    精度：不得高于来源实际提供的精度。
```

合法组合示例：

```text
observed_at_utc
period_start_at_utc
effective_session_date_market
expiry_at_utc
recorded_at_utc
horizon_calendar_day_utc
```

新合同，以及既有 class 新增或修改的 registration，不准入 `date`、`timestamp`、`as_of`、`generated_at`、`report_date` 等裸名或依赖上下文的名称。既有字段仅在当前 code-owned exact registration 已明确绑定 role 和 storage form 时，作为兼容项继续有效。调用方按登记解释字段，不能从裸名推断。该 exact row 由 Software Delivery 管理的 migration 取代或退役之前保持有效；没有 exact registration 的既有字段仍然 fail closed。当前兼容字段清单由代码维护。

外部 Source 仅提供日期时，领域使用已准入的 date storage，或使用明确记录 precision 与 timezone metadata 的保守投影。保守投影不得被表述为精确事件时间点。

### Timestamp §2 · 稳定的 Role Vocabulary

产品使用九种 role，代表八个 concept。Interval start 与 end 是两个独立 role，共同表达一个成对区间概念。

| Role | 含义 | 条件与边界 |
| --- | --- | --- |
| `observed_at` | 事件发生，或材料在外部世界或领域中变得可观察的时间。 | 与本地存储该材料的时间区分。 |
| `period_start_at` | 覆盖区间包含端点的起始时间（inclusive start）。 | 与 `period_end_at` 配对。 |
| `period_end_at` | 按所属区间政策确定的结束时间。 | 与 `period_start_at` 配对，并满足先后顺序要求。 |
| `effective_at` / `effective_date` | rule、policy、appointment、decision 或 state 开始适用的时间。 | 与公告或记录该项内容的时间区分。 |
| `expiry_at` / `expiry_date` | authority、rule、grant、request 或 validity window 停止适用的时间。 | 与安排未来工作的时间区分。 |
| `recorded_at` | 权威存储原子提交该记录的时间。 | 只能由该 store 分配；caller、worker 和 provider 不能代为分配。 |
| `updated_at` | 可变记录或投影最后一次变化的时间。 | Immutable event 和 archive record 禁止使用。 |
| `horizon_date` | 内容或数据在实质上保持 current 的最晚日期。 | 与发布时间或提交时间区分。 |
| `scheduled_for_at` | 系统计划执行未来工作的时间。 | 与 expiry、deadline 或有效期终点区分。 |

每个持久化 record 都有 `recorded_at_utc`。没有独立持久化的 embedded immutable value 可以依赖所属 record；它不得复制该提交时间，仿佛自己具有第二个 record identity。

Immutable fact 通过追加新 record 表达。Mutable projection 可以使用 `updated_at_utc`，其 source event chain 继续作为权威依据。`received`、`issued`、`requested`、`committed`、`projected` 和 `built` 描述动作，不增加新的 timestamp role；所属 record 的 `recorded_at_utc` 表示它的权威提交。

### Timestamp §3 · 稳定的 Storage Form

| Storage suffix | 含义 | 表示要求 |
| --- | --- | --- |
| `_at_utc` | UTC 时间线上的一个时间点（instant）。 | 带 UTC offset 的 RFC 3339 / ISO 8601 value；canonical form 使用 `Z`。 |
| `_calendar_day_utc` | UTC 日历中的一天，通常用于 24/7 领域。 | ISO date：`YYYY-MM-DD`。 |
| `_session_date_market` | 特定领域或资产的市场交易日。 | ISO date，并提供 sibling IANA `market_tz` 及所属 calendar policy。 |

Role 与 storage 的兼容要求如下：

| Role | 允许的存储及条件 |
| --- | --- |
| `recorded_at`、`updated_at`、`scheduled_for_at` | 仅使用 `_at_utc`。 |
| `period_start_at`、`period_end_at` | 同时出现并使用相同 storage family；instant interval 使用 `_at_utc`，session interval 使用共同的 session-date form。 |
| `effective`、`expiry` | 精度为 instant 时使用 `*_at_utc`；精度为 date 时使用 calendar 或 session date form。 |
| `horizon_date` | 使用 calendar 或 session date form，不能虚构 instant。 |
| `observed_at` | 通常使用 `_at_utc`；日期精度的观察使用已准入的 date representation，或显式类型化的 conservative projection。 |

Instant 与 date 不能互换。Midnight、end-of-day、market close 和 session membership 属于领域转换，必须具有显式 calendar、timezone、precision policy 和 typed converter。

### Timestamp §4 · 由代码持有的 Per-class Registration

Timekeeping Class Registry `[Time-Registry]` 持有精确的 class-by-role matrix。每个已注册 class 为每种 role 指定一种状态：

```text
REQ
    要求：该 role 必须有一个 compatible field。

OPT
    要求：允许该 role 有 compatible field，但不强制出现。

FORBIDDEN
    要求：该 class 上不能出现该 role。
```

每个 concrete persisted class 都需要自己的 exact registration。Nested record 使用精确 typed class ID，lookup 必须精确匹配。未注册 persisted class、未经授权的 time field 和 wildcard class identifier 无法通过 validation，并 fail closed。

未来引入 closed-family mechanism 时，必须同时具有 typed member set、一个 owner 和显式 validator support。包含 `*` 的字符串本身不提供登记权威。

登记、predicate、converter、calendar 和 distributed-clock profile 的实际实现、准入事实及覆盖情况，只由所属代码与生成视图提供。生成的 matrix projection 用于展示当前登记；复制到 Design Doc、schema comment、Skill 或 UI 的表格不取得 registration authority。逻辑事实入口为 `logical:timestamp_semantic_registry` 与 `logical:timestamp_comparison_validator`，具体项目提供对应实现。

### Timestamp §5 · Clock Domain

Clock domain 标识哪个权威来源产生了一项时间声明，以及该声明具有哪些误差或排序保证。

| Clock 或 chronology | 允许提供的依据 | 边界 |
| --- | --- | --- |
| Authoritative store clock | 在 atomic commit 时分配该 store 的 `recorded_at_utc`。 | 提交时间属于该 store。 |
| External Source clock | 在具有 provenance 和 declared precision 时支持 `observed_at`。 | 不能替代 local commit time。 |
| Worker 或 process wall clock | 在 admitted profile 下调度或观察本地工作。 | 不能分配其他 store 的权威提交时间。 |
| Provider timestamps | 提供 observational execution evidence。 | 取得其他用途前，必须由 typed domain projection 明确准入。 |
| Durable backend history time | 提供基础设施执行历史的时间顺序。 | 不自动成为 domain event、Artifact freshness anchor 或 Runtime ledger commit time。 |
| Monotonic process clock | 测量本地 duration 和 timeout。 | 不能作为跨进程 business timestamp 持久化。 |

UTC representation 只说明表示方式。两个 service 都输出 UTC，仍可能具有不同 uncertainty 和 clock health。跨权威 ledger 的排序，在可用时使用 immutable causal reference 与 monotonic version 或 high-water mark；wall-clock time 不能替代因果顺序。

### Timestamp §6 · Comparison Law

默认合法比较同时满足：semantic role 相同、storage 兼容、适用时已声明 calendar，以及 clock-domain relationship 已准入。下表各行约束对应类型的所有比较，包括同类直接比较。Date-to-instant、跨 role、跨 calendar 或跨 clock 的比较还须满足相应的显式转换或注册 predicate 条件。未满足这些条件时，禁止直接比较原始值。

| 比较情境 | 必须满足的条件 |
| --- | --- |
| Instant comparison | 在 UTC 时间线上进行。 |
| Calendar-day comparison | 使用相同 calendar meaning。 |
| Session-date comparison | 使用相同 market timezone 和 calendar policy。 |
| Date-to-instant 或 session-to-instant | 使用具名 typed conversion；调用方不能自行指定 midnight 或 close。 |
| Cross-role comparison | 使用已注册 predicate，具有固定 business meaning 和 typed operand。 |
| Cross-calendar 或 cross-clock comparison | 使用已注册的 typed converter 或 protected predicate，保持 calendar 和 clock-domain 要求。 |
| Validity interval | 默认采用半开区间；所属 contract 显式注册其他语义时才可例外。 |

默认有效区间保持：

```text
effective <= t < expiry
```

Semantic mismatch、missing converter、unknown calendar 或 incompatible clock profile 必须抛出 typed error。不能将这些失败静默降级为 boolean、`UNKNOWN` 或相近的 fallback；实际接口的错误码和处理动作由所属代码合同定义。

#### Timestamp §6.7 · Protected Predicates

受保护的跨角色或跨时钟决定，使用由代码注册的具名 predicate。每项 registration 绑定以下内容：

- operand role 与 storage form；
- calendar 与 clock domain；
- distributed-clock profile 及 health-evidence requirement；
- comparison meaning 与 permitted operation purpose。

准确 predicate ID 和当前覆盖范围由 code-owned predicate registry 及生成视图提供。Caller 使用已注册 predicate，不在 SQL、adapter、prompt 或 local utility 中复制比较逻辑。Cross-clock predicate 同时遵守 `Timestamp §8` 的保守有效窗口。

只验证 timestamp syntax 的 storage-wrapper helper，不能授权 protected decision，也不能单独证明任何 protected cross-clock action 符合本合同。`Timestamp §6.7` 保留为授权与 Runtime 合同使用的稳定逻辑锚点。

### Timestamp §7 · Timezone 与 DST Law

Local civil time 使用 IANA timezone identifier。`-05:00` 这样的 fixed offset 不能代表会随夏令时改变 offset 的地区。

| 情境 | 处理要求 |
| --- | --- |
| 持久化时间点 | 保存 UTC instant，同时保留解释 local wall-clock intent 所需的 IANA timezone 或 calendar identity。 |
| 解析 market-session date | 使用所属 exchange 或 domain calendar，覆盖 holiday、early close 和 session boundary。 |
| 不存在的 spring-forward time，或有歧义的 fall-back time | 仅由显式注册 policy 解析；结果记录 timezone 与 disambiguation decision，或拒绝 input。 |
| Physical-hour lookback | 使用 UTC instant 或 monotonic duration；不能使用 local wall-clock arithmetic。 |
| Business day 或 session 计算 | 使用所属 calendar；不能加减固定天数代替。 |
| Scheduler timezone、task cadence、market anchor | 由所属 T1 scheduler 或 domain contract 选择。 |

Parser 使用标准 timezone 和 ISO 8601 implementation，并将 parser failure 转为 typed semantic error。手写 timezone allowlist、fixed-offset substitution 或不完整 timestamp regex 不能代替验证。

### Timestamp §8 · Distributed Clock Safety

当 authorization、grant、lease、execution fence 或其他 protected action 比较不同 clock domain 提交的 instant 时，operation 固定使用一个 immutable `DistributedClockProfile`。

```text
DistributedClockProfile
    适用：受保护动作需要比较不同 clock domain 的 instant。
    性质：不可变，由 operation 固定使用。
    内容：参与的 clock domain、admitted time source、每个 domain 的 maximum uncertainty、
          conservative safety margin、required clock-health evidence、freshness policy、
          适用的 predicate 与 operation purpose，以及 fail-closed behavior。
    数值依据：由 deployment profile 提供 measured numeric bound；本合同不设 universal skew constant。

ClockHealthEvidence
    提供方：每个参与 service。
    性质：fresh、immutable。
    内容：source、measured offset、uncertainty、health result、observation time、
          validity end、authoritative commit time 与 profile identity。
    引用：protected record 通过 exact ID 与 hash 引用 profile 和 evidence。
```

Protected predicate 仍比较两个或更多 clock-domain instant 时，authoritative commit 仅在下列保守半开窗口内被接受：

```text
effective_at_utc + safety_margin
    <= recorded_at_utc
    < expiry_at_utc - safety_margin
```

Profile 或 health evidence 出现 `missing`、`expired`、`unhealthy`、`regressed`、`mismatched` 或 `unverifiable` 中任一种情况，均须 fail closed。

**免于上述窗口的条件：** Product Authorization owner 可以准入一个 product-owned online protocol，使某个 registered protected predicate 的 decision input 完全不再作 cross-clock instant assertion。该例外必须同时满足：predicate registration 明确记录这一事实；Product Authorization contract 定义替代 evidence 和 fail-closed result。Caller、adapter 和 Module 无权自行声称例外。只要 operation 仍然比较 cross-clock instant，profile、health evidence 和保守窗口的全部义务继续适用。

Monotonic authority version 与 event high-water mark 只建立因果顺序，不能证明 clock health 或 validity。Synchronized clock 也不能证明因果顺序、current authorization 或 single-writer fencing。Protected distributed decision 需要所属 contract 指定的每一种 evidence；符合一种要求不替代其他要求。

## 4. Capability and Operation

### 4.1 区分登记修改与语义修改

| 修改对象 | 所属工作与采用条件 |
| --- | --- |
| 普通 class registration，或 `REQ`、`OPT`、`FORBIDDEN` row | 属于 production code-and-schema change。领域负责人定义 row 的领域含义；Software Delivery 负责 Code Design、确定性验证、独立 engineering review 和 release admission。未改变稳定语义时，无需编辑本 T0。 |
| 稳定 role、storage form、comparison meaning 或 clock invariant | 先形成 Timestamp Semantics Design candidate，按 DDM 进行独立 Design review，并取得 Timestamp Semantics owner 的明确决定。 |
| Constitutional commitment | 在上述语义修改之外，还需 Charter amendment；普通登记修改不因此成为宪制修订。 |

明确授权的新建或修订请求可以直接进入 DDM 方法；已有已审 `SystemChangePlan` 时附对应步骤。通用文稿检查、独立 `design_contract_reviewer` 和审核结果使用遵守 [Design Doc Management](the_design_doc_management.md)；共同审核纪律采用 [Review Contract](the_review_contract.md)。专业规则是否满足、Design 审核结果、owner 决定和软件采用分别保留实际结果。

## 5. Dependencies and Verification

时间语义的符合性检查覆盖本合同定义的 role、storage、exact class、predicate、converter、calendar、DST 和 distributed-clock 条件。Schema validator 消费代码持有的 registry；实际检查覆盖情况由代码与生成视图提供。发现语义不匹配时，交回真实 schema 或代码负责人修复。

### 5.1 尚待确定的配套设计

以下配套设计尚未确定。本规范不把它们视为已经交付，也不要求作者在本次文字整理中选择具体实现。

| 待确定事项 | 决定与承接负责人 | 决定前的影响和处理 |
| --- | --- | --- |
| Exact persisted-class registration 的 release 与 compatibility model | Timestamp Semantics owner 确认共同兼容要求，采用项目的 registry 代码负责人形成实现合同；尚无实现负责人时，由采用项目 owner 指定。 | 已有 exact row 按 Timestamp §1 继续有效，直到经 Software Delivery 的迁移取代或退役。新发布或兼容机制须先取得相应决定，不从本文猜测版本规则。 |
| Semantic-role 与 distributed-clock predicate registry 的 service ownership 和 versioning | Timestamp Semantics owner 确认语义责任，采用项目 owner 指定服务和代码负责人；负责人按对应项目设计明确服务归属与版本方案。 | 沿已有登记的准确来源使用 class、predicate 和 profile。改变服务归属或版本模型前补齐决定，不能以未知为由建立平行权威。 |
| Class、predicate 与 clock-profile coverage 的公开 generated-inspection schema | Timestamp Semantics owner 明确需披露的共同性质，采用项目的 registry/inspection 代码负责人定义输出 schema；负责人未定时由项目 owner 指定。 | 当前事实使用已有代码输出及其声明 schema，不承诺尚未定义的跨项目统一字段。消费者缺少所需视图时，交给该提供方补齐并说明未验证范围。 |

## 6. Peer Boundaries

| 相关方 | 消费本合同的内容 | 对方保留的职责 |
| --- | --- | --- |
| Design Doc Management | 本合同的对象、决定范围和所需结果。 | Design 层级规则、`design_contract_reviewer` 的标准、结果含义和候选审核要求。 |
| System Change Governance | 时间语义修改的范围；已有计划时提供对应步骤。 | 计划范围、影响面、依赖顺序、负责人、写作方法、Reviewer 和完成计划；不把计划设为直接授权 Design 请求的额外前提。 |
| Product Authorization | 受保护 authorization 与 grant 的时间角色、跨时钟比较及本合同规定的例外条件。 | user_key 数据库权限、allow/deny 及权限分配与撤销；本合同不增加其产品权限对象。 |
| Agent Runtime | execution、lease、retry、recovery record 的时间角色、时钟、排序和 fencing 要求。 | Module 与 Workflow 执行、Attempt、retry、recovery 和 Runtime record 所有权。 |
| Data Governance | retention、migration、backup、restore、destruction 使用的时间角色和比较规则。 | 数据政策、residency、retention duration、迁移与销毁决定。 |
| Software Delivery | code、schema、build、release、deployment、rollback、retirement record 的时间角色，以及精确登记与分布式时钟要求。 | Code Design、确定性验证、独立工程审核，以及发布、部署、迁移、回滚和退役生命周期。 |
| Agency Platform | service 与 record 共同使用的时间含义。 | service hosting、composition 和项目具体实现。 |

第 3 章 Timestamp §8 的 online protocol 条款只规定例外成立的完整条件，不证明某个当前消费者已经具备该协议。只有对应产品合同与 predicate registration 明确满足该条款时，才使用例外；本次整理不创建替代协议。

## 7. References

- `[T0-Charter]` Project Charter：`designDoc/the_charter.md`，由消费项目提供。
- `[T0-DDM]` [Design Doc Management](the_design_doc_management.md)
- `[T0-Change]` [System Change Governance](the_system_change_governance.md)
- `[T0-Authz]` [Product Authorization](the_product_authorization.md)
- `[T0-Runtime]` [Agent Runtime](the_agent_runtime.md)
- [Agency Platform](the_agency_platform.md)
- [Data Governance](the_data_governance.md)
- [Software Delivery](the_software_delivery.md)
- [Review Contract](the_review_contract.md)
- `[Time-Registry]` 项目本地且由代码持有的 timestamp semantic registry；逻辑入口为 `logical:timestamp_semantic_registry`。

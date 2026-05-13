---
title: Crypto Project Expert Digestion Seed
status: active_draft
reader_persona:
  - Research Architect
  - Crypto Project Analyst
  - Analysis Platform Builder
source:
  - new_files/加密货币项目双轨分析标准模板（最终永久版）.pdf
  - new_files/crypto_dual_track_framework_feedback.md
---

# Crypto Project Expert Digestion Seed

## 1. 这是什么

本文定义 `digestion` layer 的 `crypto_project_expert` 子系统种子。

它不是一份单个 token 的研究报告，也不是对原 PDF 的修改意见。它把原 PDF 的“双轨分析”升级成一个可复用的 Crypto Project Expert：先判断公开证据能支持什么，再按项目类型调用模块，最后输出可供 thesis / watchlist / portfolio workflow 消费的项目级判断资产。

核心定位：

```text
read_content.md / public source packet
  -> Crypto Source Card
  -> Typed Crypto Claim
  -> Dual Track Read
  -> Crypto Decision Brief
  -> Thesis / Theme / Portfolio Decision
```

`crypto_project_expert` 位于 `Research Promotion / Digestion` 层。它负责把材料变成可审计、可复用的中间判断，不直接批准 thesis，也不直接给 portfolio action。

## 2. Reader End-State

读完本设计后，下游 agent 应能判断：

- 何时把 crypto 项目材料送入 `crypto_project_expert`。
- 如何区分公开可查证据、公开 proxy 推断和公开资料无法确认的信息。
- 如何把项目分析拆成 `Survival / Fundamental Track` 与 `Reflexive Market Track`。
- 如何按项目类型调整权重，而不是自动套一张大模板。
- 如何把两轨合并为 `participation_status`、price bands、invalidation triggers 和 confidence。
- 何时把结果交给 thesis / portfolio 层，何时只保留为观察或 blocked result。

Silent violation:

```text
报告给出一串价格目标和操盘叙事，但没有标明哪些来自公开证据、哪些只是 proxy、哪些公开资料无法确认。
```

## 3. Admission Boundary

进入 `crypto_project_expert` 的材料应满足至少一项：

- 涉及某个 token / protocol / crypto project 的长期生存、估值、代币供给或参与资格。
- 涉及项目级 market structure：流通盘、解锁、筹码、CEX/DEX 流动性、perp OI、funding、叙事热度。
- 涉及可复用 crypto 项目分析方法，而不是单次行情评论。
- 需要把公开资料拆成 `public observable / proxy / unknown` 三类。

不进入：

- 单日价格波动。
- 纯短线交易信号。
- 没有可审计项目材料的 meme 口号。
- 已经属于 portfolio execution 的仓位动作。

## 4. Evidence Permission Layer

Crypto Expert 的第一道防火墙是证据权限。每条结论先标注证据类型，再决定可用程度。

```text
1. publicly_observable
   公开可查，必须尽量填。
   例：token supply、unlock schedule、合约、链上地址、TVL、fee、volume、CEX/DEX 流动性、funding、公开融资轮次、审计报告、官方 docs。

2. proxy_inferable
   不能直接知道，但可以用公开 proxy 粗略判断。
   例：卖压、机构成本、真实用户质量、做市强度、叙事热度、筹码集中度、流动性承接能力。

3. not_knowable_from_public_data
   公开信息无法确认，必须标 unknown / cannot know。
   例：OTC 真实成交成本、做市商内部协议、基金真实 LP 压力、团队真实卖币计划、交易所上币排期、私下锁仓补充协议。
```

硬规则：

- 公开资料拿不到的信息不能写成确定结论。
- 需要非公开信息才能成立的判断，置信度最高只能到 `medium`，多数应为 `low`。
- `cannot_know` 不是失败，而是防止伪精确的必要输出。

## 5. Typed Claim And Source Firewall

### 5.1 Source Class

初始 `source_class`：

| source_class | 可支持 | 不能直接支持 |
|---|---|---|
| `official_project_disclosure` | roadmap、tokenomics、team 声明、treasury 披露 | 真实用户质量、真实收入质量 |
| `onchain_data` | holder concentration、flows、active addresses、contract state | 用户动机、真实控制人 |
| `exchange_market_data` | liquidity、depth、funding、OI、liquidations | 项目基本面价值 |
| `security_audit` | 已知安全风险、未修复漏洞、审计覆盖 | 未来绝对安全、市场 upside |
| `regulatory_record` | 合规风险、执法历史、许可状态 | token demand |
| `funding_unlock_record` | 融资估值、解锁窗口、潜在卖压 proxy | 一定出货、OTC 真实成本 |
| `social_sentiment` | 注意力、传播速度、retail heat | 真实需求、长期留存 |
| `third_party_research` | 候选解释、框架、交叉验证线索 | high-confidence fact without source anchors |
| `historical_case` | comparable pattern、情景校准 | 直接 forecast |

### 5.2 Claim Type

初始 `claim_type`：

- `survival_risk`
- `treasury_runway`
- `security_risk`
- `real_usage_quality`
- `token_supply_pressure`
- `regulatory_risk`
- `competitive_moat`
- `market_heat`
- `float_structure`
- `liquidity_depth`
- `unlock_pressure`
- `reflexive_upside`
- `distribution_pressure`
- `historical_comparable`
- `decision_eligibility`

## 6. Expert Objects

### 6.1 CryptoSourceCard

Source-level prepass。回答：

- 这份材料是什么。
- 它能支持哪些 claim。
- 它不能支持哪些 claim。
- 它的时间语义和 freshness 是什么。
- 是否存在 `cannot_know` 约束。

### 6.2 CryptoClaim

Typed claim object。最少字段：

```yaml
claim_id: <id>
source_ref: <source>
source_class: <source_class>
claim_type: <claim_type>
claim: <short statement>
evidence_permission: publicly_observable | proxy_inferable | not_knowable_from_public_data
evidence_refs: []
proxy_used: []
cannot_know: []
confidence: low | medium | high
confidence_cap_reason: <why capped, if any>
freshness: current | stale | unknown
invalidation_triggers: []
```

### 6.3 DualTrackRead

项目级 read。包含：

- `Survival / Fundamental Track`
- `Reflexive Market Track`
- `Track Merge`
- `Data Gaps`
- `Structural Unknowns`

### 6.4 CryptoDecisionBrief

给 thesis / watchlist / portfolio workflow 消费的输出，不是 portfolio action。

```yaml
participation_status: prohibited | observe_only | small_probe | participate | core_candidate
best_use_case: long_term_hold | cycle_trade | event_driven | reflexive_trade | avoid
price_bands:
  fundamental_floor: <range or unknown>
  bear_case_downside: <range or unknown>
  reflexive_upside: <range or unknown>
  distribution_pressure_zone: <range or unknown>
invalidation:
  fundamental_invalidation: []
  market_structure_invalidation: []
  liquidity_invalidation: []
confidence:
  high_confidence_facts: []
  proxy_estimates: []
  structural_unknowns: []
handoff:
  allowed_downstream: thesis_candidate | watchlist | blocked | portfolio_review_candidate
  blocked_downstream: []
```

## 7. Project Type Modules

Crypto Expert 不允许“自动套所有项目”。先判定 project type，再调用对应权重。

初始类型：

- `L1_L2`
- `DeFi`
- `DePIN`
- `Meme`
- `RWA`
- `AI_token`
- `Exchange_token`
- `Identity_or_ZK`

每个类型至少定义：

```yaml
project_type: <type>
core_variables: []
low_weight_variables: []
common_misreads: []
required_public_data: []
confidence_caps: []
```

例：

```yaml
project_type: Meme
core_variables:
  - community heat
  - holder distribution
  - liquidity
  - CEX support
  - narrative spread
low_weight_variables:
  - traditional revenue
  - LTV/CAC
  - technical moat
common_misreads:
  - rejecting short-term reflexive upside solely because fundamentals are weak
```

## 8. Dogfood Contract

第一轮 dogfood 不做全宇宙覆盖。

最小闭环：

1. 选一个公开资料足够多的 token。
2. 建一个 CryptoSourceCard。
3. 生成 typed claims。
4. 生成一份 DualTrackRead。
5. 输出一份 CryptoDecisionBrief。
6. 明确哪些字段是 `publicly_observable`，哪些是 `proxy_inferable`，哪些是 `cannot_know`。

不做：

- 不给正式投资建议。
- 不写 portfolio action。
- 不把 proxy 当事实。
- 不因为某个 token 热就跳过生存和证据权限检查。

## 90. Example: 完整 Crypto Project 分析框架

本节是可复制的完整分析框架。它不是修改意见，而是 `crypto_project_expert` 的示例输出模板。

### 90.1 使用方式

收到项目名称 + 代币代码后：

1. 先判断项目类型。
2. 收集公开资料和常见付费数据源。
3. 把所有字段分成 `publicly_observable / proxy_inferable / not_knowable_from_public_data`。
4. 跑 Survival / Fundamental Track。
5. 跑 Reflexive Market Track。
6. 合并成 Decision Layer。
7. 输出 participation status、price bands、invalidation triggers、confidence 和 missing data。

如果项目类型无法判断，或关键公开资料缺失，先输出 `missing_data`，不得强行套模板。

### 90.2 可落地数据分层

```text
Publicly observable:
- token supply
- unlock schedule
- contract / explorer data
- TVL / fee / volume
- CEX / DEX liquidity
- perp funding / OI
- public financing round
- official docs
- audit reports

Proxy inferable:
- sell pressure
- institutional cost proxy
- real user quality
- market making strength
- narrative heat
- holder concentration
- liquidity absorption capacity

Not knowable from public data:
- OTC real transaction cost
- market-maker internal agreement
- fund LP pressure
- team real selling plan
- exchange internal listing schedule
- private lock-up side letters
```

### 90.3 Survival / Fundamental Track

目标：判断项目能不能活，token 有没有基本价值支撑。

#### A. 合规与法律风险

需要看：

- 主要司法管辖区风险。
- 业务模式是否可能触及证券、支付、隐私、数据、RWA 托管、KYC/AML 等规则。
- 是否有牌照、注册、法律声明或监管事件。

输出：

```yaml
regulatory_risk: low | medium | high | unknown
public_evidence: []
cannot_know: []
invalidation_triggers: []
```

#### B. Treasury / Runway

需要看：

- treasury asset composition。
- cash / stablecoin share。
- treasury 是否主要由本币构成。
- 协议收入是否覆盖运营成本。

公开资料拿不到运营成本时，不得硬算 runway；只能写 `runway_unknown`。

输出：

```yaml
treasury_runway:
  status: strong | adequate | weak | unknown
  public_evidence: []
  proxy_used: []
  cannot_know: []
  confidence: low | medium | high
```

#### C. 安全与技术可靠性

需要看：

- 审计报告。
- 未修复高危漏洞。
- 历史 exploit。
- admin key / multisig / bridge / oracle 依赖。

输出：

```yaml
security_reliability:
  status: pass | watch | fail | unknown
  known_issues: []
  missing_audits: []
  invalidation_triggers: []
```

#### D. 真实业务与收入质量

需要看：

- TVL、fee、revenue、volume。
- 真实用户留存。
- 是否依赖补贴或刷量。
- revenue 是否能进入 token value capture。

输出：

```yaml
real_usage_quality:
  status: real | subsidy_dependent | unclear | weak
  public_evidence: []
  proxy_used: []
  confidence_cap_reason: []
```

#### E. Tokenomics

需要看：

- unlock schedule。
- inflation。
- staking yield 是否来自真实收入还是 token subsidy。
- value capture mechanism。
- insider / investor / team allocation。

输出：

```yaml
token_supply_pressure:
  status: low | medium | high | unknown
  major_unlock_windows: []
  inflation_or_emission_risk: []
  value_capture_quality: strong | weak | unclear
```

#### F. Fundamental Floor

价格只输出区间，不输出伪精确单点。

```yaml
fundamental_price_bands:
  bankruptcy_or_liquidation_floor:
    range: <range or unknown>
    basis: <treasury / cash / stablecoin / cannot calculate>
    confidence: low | medium | high
  bear_case_downside:
    range: <range or unknown>
    required_conditions: []
    invalidated_by: []
  neutral_fundamental_floor:
    range: <range or unknown>
    required_conditions: []
    invalidated_by: []
```

### 90.4 Reflexive Market Track

目标：判断当前市场环境是否支持项目被炒作、拉升、分发或重新定价。

#### A. 市场周期与赛道热度

需要看：

- BTC / ETH / altcoin regime。
- stablecoin liquidity。
- sector heat。
- ETF flows。
- fear-greed / liquidation / volatility。
- social and search trend。

输出：

```yaml
market_heat:
  status: cold | warming | hot | overheated
  public_evidence: []
  proxy_used: []
  invalidation_triggers: []
```

#### B. Float / Chip Structure

需要看：

- circulating supply。
- top holders。
- exchange inventory。
- DEX / CEX liquidity depth。
- whale deposits / withdrawals。

输出：

```yaml
float_structure:
  concentration: low | medium | high | unknown
  liquid_float_estimate: <estimate or unknown>
  holder_risk: []
  cannot_know: []
```

#### C. Distribution Pressure Zone

原“机构最优出货价”改为公开 proxy 可落地版本。

```yaml
distribution_pressure:
  public_cost_proxy: <based on public round valuation / unlock / trading history, or unknown>
  unlock_pressure_window: []
  liquidity_absorption_proxy: <volume / depth / OI / DEX liquidity>
  distribution_pressure_zone: <range or unknown>
  cannot_know:
    - OTC real cost
    - market-maker agreement
    - team real selling plan
  confidence: low | medium | high
```

#### D. Reflexive Upside Scenarios

输出情景，不输出确定预测。

```yaml
reflexive_upside:
  base_case:
    price_band: <range or unknown>
    required_conditions: []
    invalidated_by: []
  upside_case:
    price_band: <range or unknown>
    required_conditions: []
    invalidated_by: []
  downside_case:
    price_band: <range or unknown>
    required_conditions: []
    invalidated_by: []
  confidence: low | medium | high
```

### 90.5 Decision Layer

两轨必须合并，不能让读者自己拼。

```yaml
final_decision:
  participation_status: prohibited | observe_only | small_probe | participate | core_candidate
  best_use_case: long_term_hold | cycle_trade | event_driven | reflexive_trade | avoid
  one_line_reason: <why>
  strongest_supporting_evidence: []
  strongest_opposing_evidence: []
  price_bands:
    fundamental_floor: <range or unknown>
    bear_case_downside: <range or unknown>
    reflexive_upside: <range or unknown>
    distribution_pressure_zone: <range or unknown>
  invalidation_triggers:
    fundamental_invalidation: []
    market_structure_invalidation: []
    liquidity_invalidation: []
  evidence_confidence:
    high_confidence_facts: []
    proxy_estimates: []
    structural_unknowns: []
  missing_data:
    fillable_gap: []
    structural_unknown: []
```

### 90.6 降级规则

```text
- 无法确认 treasury 或 runway：不能高于 observe_only。
- 存在未修复高危漏洞：不能高于 small_probe。
- 解锁压力巨大但缺少流动性承接：不能高于 small_probe。
- 收入主要来自 token subsidy：fundamental support 降一级。
- 叙事热但筹码过度集中：reflexive upside 可以保留，但风险等级升一级。
- 核心 upside 依赖非公开操盘假设：不能高于 small_probe，除非有公开市场结构证据支持。
```

## 91. Example Validation: Humanity Protocol (`H`) On Public Information

本节不是正式投资建议，只是用公开信息验证框架是否可落地。

### 91.1 Project Type

```yaml
project: Humanity Protocol
token: H
project_type: Identity_or_ZK
evidence_status: public_info_smoke_test
```

Why this type:

- Official Humanity page describes `$H` as token for programmable trust / identity verification.
- Official token page says `$H` is ERC-20 with fixed supply of 10,000,000,000.
- Official token page describes use cases around identity, validators, developers, and human-first applications.

### 91.2 Publicly Observable Facts

```yaml
publicly_observable:
  total_supply: 10_000_000_000 H
  token_standard: ERC-20
  official_allocation:
    community_incentives: 12%
    ecosystem_fund: 24%
    early_contributors_team: 19%
    identity_verification_rewards: 18%
    foundation_operations_treasury: 12%
    investors: 10%
    human_institute_strategic_reserves: 5%
  official_tge_unlock:
    community_incentives: 100%
    foundation_operations_treasury: 50%
    strategic_reserves: 5%
    team: 0%
    investors: 0%
  public_market_context:
    - OKX has Humanity / H price and educational pages.
    - Web search snippets report a large post-listing surge and major exchange attention.
```

Sources used:

- Humanity official `$H` page.
- Humanity tokenomics GitBook lockups and emissions page.
- TokenUnlocks Humanity page, marked by that site as estimated / AI-listed data.
- OKX / web search snippets for exchange attention and market heat.

### 91.3 Evidence Permission

```yaml
high_confidence_public_facts:
  - official total supply
  - official allocation percentages
  - official cliff / vesting categories
  - official token narrative and use-case claims

proxy_inferable:
  - supply pressure from allocation and unlock schedule
  - market heat from listing / price-surge articles and exchange pages
  - identity / ZK narrative category

cannot_know_from_public_data:
  - OTC real cost
  - market-maker agreement
  - team real selling plan
  - exchange internal promotion schedule
  - real quality of verified-human demand without user/revenue data
```

### 91.4 Survival / Fundamental Track Smoke Read

```yaml
regulatory_risk:
  status: medium_unknown
  reason: Identity / biometric / proof-of-humanity projects can face privacy, KYC, data, and jurisdiction-specific compliance questions.
  public_evidence:
    - official page links to privacy policy, terms, and MiCA legal statement
  missing_data:
    - jurisdiction-by-jurisdiction compliance review
    - audit of biometric / privacy implementation

treasury_runway:
  status: unknown
  reason: Public token allocation identifies foundation treasury allocation, but public source does not show operating expense or cash/stablecoin runway.
  confidence: low

security_reliability:
  status: unknown
  reason: Smoke test did not collect independent security audits or exploit history.
  fillable_gap:
    - audit reports
    - bug bounty
    - exploit history

real_usage_quality:
  status: unclear
  reason: Official use cases and identity narrative exist, but smoke test did not verify active user retention, paid usage, validator economics, or application demand.
  confidence: low

token_supply_pressure:
  status: medium_to_high_watch
  reason: Large allocations to ecosystem, team, rewards, foundation, and investors create multi-year emission / unlock monitoring need.
  public_evidence:
    - official allocation and vesting schedule
  invalidation_or_relief:
    - clear demand growth absorbing emissions
    - transparent unlock handling
```

Preliminary fundamental verdict:

```yaml
survival_verdict: observe_only
reason: official tokenomics are available, but treasury runway, real usage quality, security posture, and privacy/regulatory risk need more public evidence before investment-grade judgment.
```

### 91.5 Reflexive Market Track Smoke Read

```yaml
market_heat:
  status: hot_recently
  public_evidence:
    - OKX / web search snippets report price-tracking and exchange attention.
    - Search results report post-listing surge and major exchange listings.
  confidence: medium

float_structure:
  status: incomplete
  public_evidence:
    - official TGE unlock categories
    - TokenUnlocks page gives circulating / unlock context but marks data as estimated
  missing_data:
    - exchange inventory
    - top holder distribution
    - CEX / DEX depth
    - whale flow

distribution_pressure:
  public_cost_proxy: unknown
  unlock_pressure_window:
    - team and investor cliffs after 12 months from TGE
    - ecosystem and treasury multi-year releases
  liquidity_absorption_proxy: missing
  cannot_know:
    - OTC cost
    - market-maker agreements
    - real team / investor selling plan
  confidence: low

reflexive_upside:
  status: possible_but_unproven
  reason: identity / ZK / anti-bot narrative can attract attention, but public smoke test lacks liquidity, holder, and demand data.
  required_conditions:
    - broad altcoin risk appetite
    - visible liquidity support
    - narrative attention persists beyond listing
    - unlock pressure does not overwhelm demand
  invalidated_by:
    - falling liquidity after listing heat
    - large holder deposits to CEX
    - weak real verification / app usage
    - privacy / regulatory adverse news
```

### 91.6 Decision Brief Smoke Output

```yaml
participation_status: observe_only
best_use_case: watchlist / framework validation, not portfolio action

one_line_reason: H has a clear public identity/ZK narrative and official tokenomics, but public smoke-test evidence is insufficient on real demand, liquidity depth, holder structure, treasury runway, security posture, and regulatory/privacy risk.

price_bands:
  fundamental_floor: unknown
  bear_case_downside: unknown
  reflexive_upside: scenario_only
  distribution_pressure_zone: unknown

high_confidence_facts:
  - 10B fixed total supply
  - official allocation and vesting categories
  - identity / proof-of-humanity positioning

proxy_estimates:
  - market heat from exchange attention and listing surge coverage
  - supply pressure from official unlock structure

structural_unknowns:
  - real user demand
  - treasury runway
  - security audit depth
  - liquidity absorption
  - holder concentration
  - OTC / market-maker / insider behavior

next_public_data_to_collect:
  - CoinGecko / CoinMarketCap market cap, circulating supply, volume
  - CEX depth and perp OI / funding if listed
  - holder distribution from explorer / Arkham / Nansen if available
  - audit reports and exploit history
  - protocol usage metrics: verified users, active apps, fee / validator economics
  - unlock calendar around next cliff
```

### 91.7 What The Smoke Test Proves

This validates the framework, not the token.

The framework worked because it prevented three errors:

1. It did not turn identity narrative into proof of real demand.
2. It did not turn exchange heat into fundamental value.
3. It did not invent institution / market-maker behavior from public data.

The correct result is `observe_only`, not because H is bad, but because the public smoke test lacks enough evidence to upgrade participation status.

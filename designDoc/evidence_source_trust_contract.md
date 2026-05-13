# Evidence Source Trust Contract

**Version 0.1 — 2026-04-26**
**Status**: canonical · evidence_record schema 引此 contract 作为 `ai_verified` gate 的 trust 依据
**Charter binding**: [`the_charter.md`](the_charter.md) §III (archive 唯一事实本源) + §V (拒绝伪精度) + §VI (Evidence 必带 belief_delta)
**Related**: [`the_timestamp_semantic.md`](the_timestamp_semantic.md) v1.0
**Schema**: [`data/runtime/schemas/evidence_record_v0_2.schema.json`](../data/runtime/schemas/evidence_record_v0_2.schema.json)

---

## 0. Authority

evidence_record 的 `ai_verified=true` 是 AI 层 trust gate。要让这条 gate 不成为橡皮章，underlying source 必须可信到 AI 自动校验有真实意义。本 contract 列出 trust tier 分级 + 准入规则。

具体规则四条：

1. **R1 · `ai_verified=true` 必须有 ≥1 条 T1 source_ref**——T1 = T1A 政府/官方机构 + T1B 专业数据供应商 + T1C 受监管文件 + T1D PM-trusted 独立研究作者（curated subscription research）。仅 T2/T3 source 不足以让 `ai_verified=true`。
2. **R2 · 内部 system 引用 trust_tier=`none`**——`thesis_index` / `messages_index` / `snapshots_index` / `perplexity_log` / `themes_metadata` 都是内部 cross-reference，不构成 trust anchor。要 anchor T1 必须显式列 `system="external_url"` + 真实 T1 域名。
3. **R3 · Perplexity 自身不是 source**——它是 meta-search 工具。perplexity_log 只是 audit 工具调用。`source_refs[]` 中如要 T1 anchor，必须把 Perplexity citing 的 underlying T1 URL 作为独立 `external_url` source_ref 列出，并标 trust_tier。
4. **R4 · 永不接受的 source 一律视为 `none`**——参见 §3。

违反任何一条直接触发 charter §IV "fail loud"。schema validator 强制。

修订本 contract（含 tier 列表增减 / R1-R4 改动）门槛：跟 contract 自身改一样，走 PR + review。**不动 charter**。

---

## 1. Why this contract exists

A.2 review 暴露的 risk：`ai_verified` 当前 schema 仅是 bool，由 authoring persona 自填。verifier 跑完 Perplexity 自己翻 `ai_verified=true`，但如果 Perplexity 返回的 URLs 全是 X 帖子 / 某 Substack 个人观点，`ai_verified=true` 就成了 information laundering。

charter §V 拒绝伪精度，charter §III 要求 archive 是事实本源——这两条共同要求 evidence trust gate 必须 anchor 到外部可验证的 primary source，不接受"AI 自己在低质 source 上自校验自盖章"。

本 contract 把 trust 分级显式化，`ai_verified=true` 由分级硬约束守门。

---

## 1.5 Judgment model — AI 评分，非 hard registry

trust_tier 是 **AI categorical judgment**，不是 hard-coded URL allowlist。两个 AI 层一前一后：

1. **Caller AI**（authoring persona — verifier / adversary / drafter）写 source_ref 时自己评 trust_tier
2. **Evidence-reviewer subagent**（独立 AI）独立 re-judge 同一条 source_ref 的 trust_tier，flip `ai_verified=true` 仅当 reviewer 同意 caller 的 tier 判断

§2 给出每档**典型代表**（exemplars），不是穷举 allowlist。AI 见到一条新 source URL 时按"这个 publisher 是哪一类"做归类判断 —— 不要求 100% 字符串 match，要求 publisher identity 可识别且符合该 tier 的语义定义（政府机构 / 数据供应商 / 受监管文件 / 知名财经新闻 / 通讯社聚合）。

不接受的 case 由 §3 永不允许列表 + AI judgment 双重否认（社交媒体 / 个人 blog / 论坛 / 匿名 newsletter）。

schema 层只卡 enum 形态（`T1A / T1B / T1C / T1D / T2 / T3 / none`）+ §3 R1/R2 条件规则。**不卡 URL 字符串匹配**。

---

## 2. Trust tier 分级（5 级 + none）

### T1A — Official agency / government data

国家级 / 国际级官方机构原始数据 / 政策原文。

**美国 macro / policy / regulator：**

- 货币政策：federalreserve.gov、所有 regional Fed（newyorkfed.org / chicagofed.org / dallasfed.org / philadelphiafed.org / clevelandfed.org / atlantafed.org / stlouisfed.org / kansascityfed.org / minneapolisfed.org / sf.frb.org / richmondfed.org / bostonfed.org）、fred.stlouisfed.org
- 财政 / 税务：treasury.gov、fiscal.treasury.gov
- 经济统计：bls.gov、bea.gov、census.gov、cbo.gov
- 金融监管：sec.gov（含 sec.gov/edgar）、fdic.gov、occ.gov、cftc.gov、finra.org、ncua.gov
- 立法：senate.gov、house.gov、congress.gov、govinfo.gov
- 行政：whitehouse.gov（行政命令原文）、ustr.gov
- 能源：eia.gov、ferc.gov
- 其他：bls.gov、cdc.gov、fda.gov、ftc.gov、doj.gov

**International 央行 / 财政：**

- ecb.europa.eu、bankofengland.co.uk、boj.or.jp、bankofcanada.ca、rba.gov.au、rbi.org.in、pbc.gov.cn、snb.ch、riksbank.se、norges-bank.no、bcb.gov.br、banxico.org.mx

**多边机构：**

- imf.org、worldbank.org、bis.org、oecd.org、wto.org、un.org

**International 监管：**

- esma.europa.eu、fca.org.uk、mas.gov.sg、hkma.gov.hk、jfsa.go.jp、bafin.de、afm.nl、finma.ch

**State / local 监管（限 PUC / state securities / state PUC rate filings）：**

- 各州 PUC（puc.state.\*.us、psc.state.\*.us 等）—— 用于 utility rate cases、AI 数据中心 incremental load filings 等

### T1B — Dedicated market-data vendor

专业市场数据 / 评级 / 指数 / 结算数据。

- **Bloomberg**（terminal data + bloomberg.com 数据频道，跟 BBG news 区分）
- **Refinitiv / LSEG**（refinitiv.com、lseg.com）
- **S&P Global**（spglobal.com 含 Capital IQ）
- **Moody's** / **Fitch** / **DBRS Morningstar** / **KBRA**（评级机构正式 rating action / methodology 文件）
- **FactSet**（factset.com）
- **ICE Data Services / NYSE Group**（ice.com / theice.com / nyse.com）
- **CME Group**（cmegroup.com 含 STIR / Treasury / FX 期货 settlement / volume）
- **DTCC**（dtcc.com 结算 / repo / SCC 数据）
- **CBOE**（cboe.com vol / index 数据）
- **MSCI**（msci.com index / ESG 数据）
- **FTSE Russell**（ftserussell.com）

### T1D — Curated subscription research / trusted independent author

PM 长期订阅 + 已建立 track record 的独立研究作者。门槛比 T2 reputable journalism 高 —— 这些作者不是泛财经新闻，是 PM 主动 curate 进 archive 的研究输出，他们的 substantive analysis 经过 PM 多年 vetting。

**当前 T1D 作者 family list（与 [`data/research/source_collections.json`](../data/research/source_collections.json) 同步）：**

- **`citrini`** —— Citrini Research（含 Citrini deep research / memo posts，canonical `citrini@substack.com` / `citrini.substack.com`）
- **`citrindex`** —— Citrindex（含 automated snapshot / basket update / portfolio update mail，affiliated with Citrini）
- **`capitalflows`** —— Capital Flows（含 macro_reports / rates_fx / equity / index variants，canonical `capitalflows.substack.com`）
- **`conks`** —— Conks（含 money_markets / index variants）
- **`tmt_breakout`** —— TMT Breakout（含 wraps / index variants）

**T1D 准入规则：**

1. **正儿八经提到** —— 不是 chat-thread 一句话路由邮件，而是作者的 substantive analysis（具体 thesis / 具体数字 / 具体 mechanism）。例如 Citrini Research 的 deep memo、Capital Flows 的 macro_reports 长稿、TMT Breakout 的 wrap 摘要。chat-thread / index-style routing mail 仍属 T2 或更低（视具体内容）。
2. **必须带时间戳** —— 引这条 evidence 时必须明示 publication date：
   - 优先填入 evidence_record.observed_at_utc（事件实际发生时刻 = 作者发文时刻）
   - 或在 source_refs[].note 写明 "published <ISO 8601 UTC>"
   - 都不写 → reviewer subagent `source_trust_verdict="fail"`，因为 belief delta 时序无法 audit
3. **必须是作者 canonical URL** —— Substack 平台本身**不是** T1D；只有**该作者**的 Substack URL（`citrini.substack.com/p/<post-slug>`、`capitalflows.substack.com/p/<post-slug>` 等）才是 T1D。第三方转发 / 截图 / 摘录都按 T2 或 T3 处理。
4. **不接受第三方 paywall 转录** —— Seeking Alpha / Substack 索引页 / Bloomberg 提到这些作者的链接都不是 T1D。必须直链作者本人的 post URL。

**T1D truth semantics：**

- T1D trusted author 的 canonical substantive post 在 source-truth 层按 T1 可信锚处理。
- 该 post 中作者明确给出的事实表述、数字、机制判断、positioning read、basket definition、scenario framing，可作为 `response_supports_claim=pass` 的直接支持材料。
- T1D 不需要再找 Reuters / Bloomberg / 官方口径来证明“作者确实如此判断”。后续 reviewer 只检查：URL 是否为 trusted author canonical source、publication timestamp 是否可审计、evidence_summary 是否忠实反映作者原文、belief_delta 是否合理。
- T1D 不自动完成 PM 信念层授权。`ai_verified=true` 仍需 independent `research-evidence-reviewer` 或 PM review entry；`pm_acknowledged=true` 仍是单独 gate。
- T1D 不把作者的全部预测变成市场事实。若 evidence_summary 声称的是“作者判断 X / 作者定义 Y / 作者提出机制 Z”，T1D 可直接支持；若 evidence_summary 声称的是“市场已经发生 X / 公司已经公布 Y / 官方已经确认 Z”，仍需对应 market / issuer / official source。

**T1D 升降流程：** 新增 / 移除 family 列表走 §5 PR review 流程。当前 5 family 是 PM 显式确认的（2026-04-26）。

### T1C — Regulated filing

受监管的公司 / 投资者直发文件。

- **SEC EDGAR** 原文 filings（10-K / 10-Q / 8-K / 13F / S-1 / Form 4 / Schedule 13D/G / DEF 14A 等）
- **公司 IR portal** —— 投资者关系页面正式发布的 deck / 年报 / earnings release / 操盘手 letter（投关页 URL 必须是公司主域名 path，不接受第三方转发）
- **Earnings call transcript** —— 来源 IR 直发 / Bloomberg / FactSet / Capital IQ；不接受 Seeking Alpha 等第三方转录
- **公司新闻稿** —— IR portal 直发；不接受 PRNewswire / BusinessWire 转发版本
- **国际等价 filing**：HKEX 上市公司 announcements、TSE 上市公司 IR、SGX disclosures、FCA company filings 等

### T2 — Reputable journalism

知名财经 / 政经新闻；**仅当与 T1 source 配引用时**才能让 `ai_verified=true`。T2 单独不足。

- **Reuters**（reuters.com）
- **Wall Street Journal**（wsj.com）
- **Financial Times**（ft.com）
- **New York Times**（nytimes.com — business / economy desk only）
- **Bloomberg News**（bloomberg.com news 部分 — 跟 T1B 的 BBG terminal 数据区分）
- **Politico**（politico.com）
- **The Economist**（economist.com）
- **Barron's**（barrons.com）
- **Nikkei Asia**（asia.nikkei.com）
- **South China Morning Post**（scmp.com — 限政经版块）

### T3 — Wire / aggregator

通讯社 wire / 二级聚合 / 财经门户。任何情况下 `ai_verified=false`。

- **AP / AFP / Kyodo / Xinhua wire**
- **CNBC**（cnbc.com）
- **Yahoo Finance**（finance.yahoo.com）
- **Investing.com**
- **MarketWatch**（marketwatch.com）
- **Forbes**（forbes.com）
- **Business Insider**（businessinsider.com）
- **Seeking Alpha**（seekingalpha.com）
- **The Street**（thestreet.com）
- **CNN Business**（cnn.com/business）

T3 用于"补色 / 时序定位 / cross-window 验证"是允许的，但不足以单独 anchor verification gate。

### `none` — 内部 cross-reference + 永不允许的 source

**内部 system（trust_tier 始终 `none`）：**

- `thesis_index` / `messages_index` / `snapshots_index` / `perplexity_log` / `themes_metadata` —— 这些是 repo 内部 cross-reference，不是外部 trust anchor
- `image_reviews`、`broker_record` —— 内部生成数据（之前 enum 已收紧不再列）

**永不允许 anchor `ai_verified=true` 的 source（trust_tier 强制 `none`）：**

- Twitter / X posts / Mastodon / Bluesky 等社交媒体（所有平台、所有作者，无例外）
- Substack / Medium / 个人 blog（T1D trusted author canonical substantive post 除外）
- Reddit / 论坛 / Discord / Telegram / WhatsApp leak
- 未注明 author 的匿名 newsletter
- LinkedIn posts
- YouTube video（含 podcast 自动转录）—— 例外：当 IR portal 直链 YouTube 是 earnings call 的官方录像，按 T1C 处理
- 个人观点 newsletter / Substack 付费订阅 letter（除非已签约的 sell-side notes —— 这类属另一类 source_type，不在本 contract 覆盖）

---

## 3. `ai_verified=true` 准入规则（schema-enforced）

`evidence_record.ai_verified=true` 必要条件 (R1)：

1. `source_refs[]` 中 ≥1 条 entry 满足 `trust_tier ∈ {T1A, T1B, T1C, T1D}`
2. 该条 entry 的 `system="external_url"`（内部 system 即使指向 T1 内容也不算 anchor，必须显式列 external URL）

充分条件 (R3，B.0.5/B.0.7 落地)：

3. `ai_review_log[]` 中 ≥1 条独立 reviewer subagent (`research-evidence-reviewer`) 或 PM (`pm`) 写的 entry `final_verdict="verified"`

schema v0.2 用三条 conditional rules 强制（R1 + R2 + R3）。详见 [`data/runtime/schemas/evidence_record_v0_2.schema.json`](../data/runtime/schemas/evidence_record_v0_2.schema.json) 的 `allOf` block。

R1 必要 + R3 充分共同决定 `ai_verified=true`：caller AI 写 source_ref + tier，独立 research-evidence-reviewer subagent re-judge tier + belief_delta + content support；reviewer 同意才能翻 ai_verified=true。authoring persona 自己 flip ai_verified=true 不再合法（reviewer_persona enum 排除 authoring 五人）。

---

## 4. trust_tier 用法范例

### 范例 1 — verifier 引 Fed.gov 演讲（T1A）

```jsonc
"source_refs": [
  {
    "system": "thesis_index",
    "id": "warsh_succession_reanchors_forced_pause_factor_a",
    "trust_tier": "none",
    "note": "thesis 内部链"
  },
  {
    "system": "perplexity_log",
    "id": "williams_jefferson_silence_2026_04_21_to_24_null_finding",
    "trust_tier": "none",
    "note": "verifier null-finding 调用 audit"
  },
  {
    "system": "external_url",
    "id": "https://www.federalreserve.gov/newsevents/speech/waller20260417a.htm",
    "trust_tier": "T1A",
    "note": "Waller 4/17 'One Transitory Shock After Another' 演讲原文"
  }
]
```

`ai_verified=true` 合法 —— external_url + T1A 锚定。

### 范例 2 — verifier 引 Vernova IR（T1C）

```jsonc
"source_refs": [
  {
    "system": "thesis_index",
    "id": "hyperscaler_grid_procurement_tightens_power_equipment",
    "trust_tier": "none"
  },
  {
    "system": "external_url",
    "id": "https://investors.gevernova.com/q1-2026-earnings-call-transcript",
    "trust_tier": "T1C",
    "note": "Vernova IR 直发的 Q1 2026 earnings call transcript"
  },
  {
    "system": "external_url",
    "id": "https://www.eei.org/issues-and-policy/load-growth/2026-04-quarterly-summary",
    "trust_tier": "T2",
    "note": "EEI 2026-04 quarterly summary —— 行业协会，T2"
  }
]
```

`ai_verified=true` 合法 —— Vernova IR T1C anchor。EEI 是 T2 但因为 T1C 已存在，T2 用于 cross-window 补色 OK。

### 范例 3 — 不可 ai_verified=true 的 case

```jsonc
"source_refs": [
  {
    "system": "thesis_index",
    "id": "...",
    "trust_tier": "none"
  },
  {
    "system": "external_url",
    "id": "https://twitter.com/some_handle/status/1234567890",
    "trust_tier": "none",
    "note": "X post —— §3 永不允许"
  },
  {
    "system": "external_url",
    "id": "https://www.cnbc.com/article/2026-04-25-some-news",
    "trust_tier": "T3"
  }
]
```

`ai_verified` 必须 `false` —— X post 强制 none，CNBC 是 T3 不能 anchor。这条 evidence_record 仍然有效（archive 接收），但不能驱动信念层 transition（charter §II + R1）。

### 范例 4 — Adversary 自观察（T3 / inferred）

adversary 基于本地 archive pattern 写的 counter_evidence 通常没 external T1 anchor —— 这种就该保持 `ai_verified=false`，`source_quality="inferred"`，`confidence="exploratory"`。这是 schema 在阻止 adversary 把"我直觉"包装成 ai_verified evidence。如果 PM 看完确实信，可以走 `pm_acknowledged=true` 路径手动 ack（PM ack 不依赖 ai_verified）。

---

## 5. Tier 升降流程

发现 source 应改 tier（如 Reuters 被认定 T1B 而非 T2，或某新数据供应商应入 T1B）：

1. 发起 PR 改本 contract §2 列表 + 增加 rationale prose
2. PR 标 `evidence-source-trust-contract` label，至少 1 PM review
3. merge 后，validator 端在下个 schema 版本（L3）经 registry 反映；当前 L2 阶段仅靠 caller 自填 + research-evidence-reviewer subagent 校验

新增**永不允许**类（§3）门槛较低：发现某社交平台 / 新型聚合源应禁，可直接 PR 加入。

---

## 6. 与其他 contract 的关系

- **the_timestamp_semantic.md**：本 contract 不改 evidence_record 的时间字段；时间字段仍按 timestamp contract §4 矩阵 evidence_record 行（recorded_at REQ + updated_at REQ + observed_at OPT）
- **charter §III（archive 唯一事实本源）**：archive 仍是事实本源，本 contract 不让 evidence_record 复制 archive 内容；只确保 evidence_record 的 source_refs 真的 anchor 到 external T1 source
- **charter §V（拒绝伪精度）**：trust_tier 是 enum，不是 float trust score。永远不接受 `trust_score: 0.78` 这种伪精度
- **charter §VI（Evidence 必带 belief_delta）**：本 contract 与 belief_delta 正交 —— belief_delta 描述信念变化，trust_tier 描述 source 可信度。两条都必须满足

---

## 7. v0.1 → v0.2 演进路径

当前 L2 阶段：trust_tier 是 caller AI 评分 + research-evidence-reviewer subagent 独立 re-judge。

v0.2 演进**不引入** hard-coded URL registry —— AI judgment 已经覆盖大多数 case，硬编码 maintenance 成本 / 修订门槛会让新 publisher 进入面变慢。

v0.2 增量改进可能包括：

- research-evidence-reviewer subagent 加 `tier_rationale` prose 字段（reviewer 必须用一句话解释为何评定为 T1A vs T2，强迫显式判断而非 rubber-stamp）
- 累计 review 数据后，把高频被错评的 publisher 整理成 reviewer 端的 prompt-side reference（reviewer 看到熟悉的 publisher 可以快速判断，但仍然是 AI judgment 不是 schema enforcement）
- 跨 reviewer 一致性抽查（同一条 source_ref 多个 reviewer 评出不同 tier 时 escalate 给 PM）

**永远不会做：URL allowlist 硬编码 / domain registry 自动 derive**。AI judgment 是本 contract 的 design choice，不是过渡方案。

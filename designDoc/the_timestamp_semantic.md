---
title: Timestamp Semantic Contract
status: active
layer: T0
t0_layer_id: the_timestamp_semantic
canonical_owner: designDoc/the_timestamp_semantic.md
---

# Timestamp Semantic Contract

**Version 1.0 — 2026-04-26 (T0 restructure)**
**Status**: canonical · 任何含时间字段的设计 / schema / API 必须先经本 contract
**Charter binding**: [T0-Charter] §IV (fail loud) + §VI (belief delta) + §VII (freshness law)
**Repo-local projection of `09_soul/axioms/t11_timestamp_semantics_explicit.md`.**

> **Migration phase as of 2026-05-06**: legacy alias read path remains open until 2026-05-19; write path has stopped. New schemas and code must follow this contract now.

---

## 0. Contract Capsule

Machine-audit block. Keep paths, ids, aliases, commands, and ledger pointers plain; use citation ids only in body prose and `References`.

```yaml
layer: T0
t0_layer_id: the_timestamp_semantic
status: active
canonical_owner: designDoc/the_timestamp_semantic.md
scope: T0 authority gate for timestamp/date field semantics across the repo, including role taxonomy, storage suffix vocabulary, per-class matrix, comparison contract, DST handling, and validation hygiene
non_goals:
  - object ontology, task routing, and non-time fields
  - artifact freshness predicate semantics, which belong to the_artifact_graph
  - schema admission outside time fields
  - TradeCLI code-admission discipline, which belongs to the_tradecli_code_management
inputs:
  - 09_soul/axioms/t11_timestamp_semantics_explicit.md
  - designDoc/the_charter.md
  - data/runtime/schemas/*.json
outputs:
  - timestamp role taxonomy
  - storage suffix vocabulary
  - per-class registry matrix
  - comparison, DST, and validation contract
truth_surfaces:
  - src/core/timekeeping/**
  - src/data_update/session_freshness.py
  - src/tools/timeaudit.py
  - src/cli/tradectl.py
  - tests/test_timekeeping.py
  - tests/test_timeaudit.py
  - data/runtime/schemas/*.json
runtime_triggers: see Machine Audit Runtime Surfaces
downstream_consumers:
  - all schemas and runtime modules with timestamp/date fields
  - artifact graph freshness checks that use timestamp/date fields
  - charter alignment and timekeeping canonicalization initiatives
  - ingestion, research, digestion, and operation T1 docs that define time-bearing objects
open_decisions:
  - legacy alias read path closes on 2026-05-19
  - backfill CLI for legacy aliases remains proposed until cutover
  - per-class schema validator coverage must be checked when each matrix row changes
review_gate: design-doc-reviewer
runtime_surface_ledger: see Machine Audit Runtime Surfaces
verification_hooks: see Machine Audit Runtime Surfaces
```

## 0.1 Authority

**Analyst Billie 中所有 timestamp / date 字段必须先经本 contract，再进任何下游 schema、API、design doc、code。**

具体规则三条：

1. **R1 · 全局必填 `recorded_at_<storage>`**——任何进入我方系统的 record 必有"我方写下来的时刻"。这是 archive-first 的最低承诺，无例外。
2. **R2 · class 必先登记**——新增 object class 进仓前，必须在 §4 per-class registry 添加一行声明 9 列三态（REQ / OPT / —）。未登记的 class 不允许写入任何 schema。
3. **R3 · 字段 ↔ 矩阵双向 enforce**——
   - 字段在 schema 但 §4 matrix 标 — → linter raise（`UnauthorizedTimestampField`）
   - 字段在 matrix 标 REQ 但 schema 缺 → linter raise（`MissingRequiredTimestamp`）
   - 字段名不符 `<role>_<storage>` 形态 → linter raise（`MalformedTimestampFieldName`）
4. **R4 · archive 层禁 `updated_at`**——charter §III 规定 archive 不可改写；archive 层 record 出现 `updated_at_*` 视为违反 immutability。overlay 层 record 必须有 `updated_at_*`。

违反任何一条直接触发 charter §IV "fail loud"，不接受 silent fallback。

修订本 contract（含 9 role 取舍 / per-class matrix 调整 / 三态语义改动）等同改 charter，按 charter §X 修宪门槛走。

---

## 1. Why this contract exists

### 1.1 历史背景：silent semantic 撞车

2026-04 之前 repo 出现过三种不同的 "date" 语义共用同一字段名 `report_date`：

- **packet JSON** 中：UTC calendar day on which the packet was built（典型 `S+1`，build 在 UTC 午夜后跑时）
- **report frontmatter** 中：ET market session this report describes（= `S`，市场实际收盘日）
- **CLI `--date`** 中：whatever the user types，无 tz 声明，直接 `strptime`

任何两个间用 `==` 比较都会产生 silent bug：

- `_report_already_finalized_after_close` 每次返回 `False`，迫使 `tradectl data update` 每天重写整个 watchlist
- `date_anchor(packet.report_date)` 在 ET-after-midnight UTC overlap 时把新 packet 误判 STALE，把未来日 packet 误判 FRESH

根因：**未命名语义** → 错的字段被传给错的比较器。本 contract 的核心修复是命名层。

### 1.2 v1.0 (2026-04-26) T0 restructure 触发

charter v1.5 收口立 Analyst Billie 为 belief revision system 后，时间字段不再仅是 packet / report 的属性——还要承载 evidence / scenario / thesis 的 belief revision 时序、portfolio decision 的 audit 链、sweeper 的 staleness 判定、artifact_graph 的 recompute 决策。

PM 在 W17 末识别："时效性是 Analyst Billie 管理的重中之重；不同 data 的重要性应按其产生 / 记录时间决定。"

→ 本 contract 从 "packet / report 字段命名规范" 升级为 **全 repo 时间字段的 authority gate**。
→ 引入 **9 role × 5 storage 双轴命名 + per-class registry 矩阵 + 三态强制**。

---

## 2. Two-axis naming convention

每个时间字段名 = `<role>_<storage>`。

```
observed_at_utc                 ← role=observed_at, storage=at_utc
period_start_at_utc             ← role=period_start_at, storage=at_utc
effective_session_date_market   ← role=effective_at/date, storage=session_date_market
horizon_session_date_market     ← role=horizon_date, storage=session_date_market
recorded_at_utc                 ← role=recorded_at, storage=at_utc
```

**禁止对象前缀**——field 名不带对象类目：

- ❌ `statement_published_at_utc` / `meeting_date_calendar_iso` / `vote_effective_session_et`
- ✓ JSON path 区分对象：`fomc_statement.observed_at_utc` / `fomc_vote.effective_session_date_et`

**禁止裸字段**：

- ❌ `report_date` / `as_of` / `date` / `generated_at` / `timestamp` / `time` 不带 suffix
- ❌ 同一字段在不同 caller 下语义不同（如 `bar_date` 时而 UTC 时而 ET）

详见 §6 anti-patterns。

---

## 3. Role taxonomy（9 roles / 8 concepts）

九个 role 各自独立、互不替代。每条 role 都过 sanity check："删掉它哪个具体决策做不了？" §3.2 将 `period_start_at` / `period_end_at` 合在一个概念节里说明；§4 matrix 仍把它们拆成两列。

### 3.1 `observed_at`

- **含义**：事件在世界中发生 / 出现的时点（point）。
- **何时用**：tick、speech delivery、vote、statement publication、policy 公布、市场行情发生、外部 source 公开发布的任何点事件。
- **何时不用**：interval 类数据（用 `period_*`）；我方系统内部产生的事件（用 `recorded_at`）；规则的生效（用 `effective_at`）。
- **存储**：通常 `_at_utc`；也可 `_session_date_et` 当事件按 session 归属。
- **决策面**：D1 currency / D2 时间衰减权重的主要 anchor。

**Date-level observed fallback**:

当外部 source 只提供日期、没有精确发布时间时，仍可写 `observed_at_utc`，但必须显式标注精度，避免把 date-level cutoff 误读成真实 publication instant。

- 精确时刻已知：`observed_precision: "datetime"`，`observed_at_utc` 写真实世界时刻。
- 只有日期已知：`observed_precision: "date"`，`observed_at_utc` 写该日期在 `market_tz` 下的 `23:59:59` 投影到 UTC 后的值。
- `observed_note` 必须说明该值是 date-level conservative cutoff，不是精确发布时间。
- `market_tz` 必须是 IANA timezone，不能用固定 offset 代替。

示例：

```json
{
  "observed_precision": "date",
  "market_tz": "America/New_York",
  "observed_at_utc": "2026-04-10T03:59:59Z",
  "observed_note": "Source only provides observed date 2026-04-09; observed_at_utc is the date-level conservative cutoff at 2026-04-09 23:59:59 America/New_York, not an exact publication time."
}
```

### 3.2 `period_start_at` / `period_end_at`（必须成对）

- **含义**：interval 类数据所覆盖的时间窗起点 / 终点。
- **何时用**：kbar（30m/1h/4h/1d）、fundamentals snapshot（fiscal quarter）、FOMC 跨会议窗、theme review 窗、sweeper 扫描窗、research coverage 窗。
- **何时不用**：point 类（用 `observed_at`）；规则有效期（用 `effective_at` / `expiry_date`）。
- **强制配对**：linter 检查到只有一个 → raise；start ≤ end 强制。
- **存储**：通常 `_at_utc`；也可 `_session_date_market` 当窗按 session 对齐。
- **决策面**：D1 currency（period_end_at 是 interval 对象的 currency anchor）；区间对齐 / 跨频率 bucketize 的对齐 anchor。

### 3.3 `effective_at` / `effective_date`

- **含义**：规则 / 任期 / 政策的生效起点。
- **何时用**：FOMC vote 生效日、Fed appointment 任期 start、关税 effective day、规则 enactment。
- **何时不用**：vote 时刻本身（用 `observed_at`，与 effective 经常 diverge——vote at T1，effective at T2）。
- **何时配 `expiry_date`**：常见——任期 / 关税 / 规则有 sunset clause。
- **存储**：当生效粒度到点时用 `_at_utc`；到日时用 `_session_date_market` 或 `_calendar_day_utc`。
- **决策面**：D3 in-force boolean。

### 3.4 `expiry_date`

- **含义**：规则 / 任期 / 政策的失效终点。
- **何时用**：Fed appointment term end、关税 sunset、规则废止日。
- **何时不用**：动态判定的"是否还有效"（用 `effective_at` + 当前时间比较）；timeout 类（用 `scheduled_for_at`）。
- **存储**：常 `_session_date_market` / `_calendar_day_utc`。
- **决策面**：D3 in-force boolean。

### 3.5 `recorded_at`

- **含义**：我方系统把这条 record 写下来的时刻。
- **何时用**：**任何 record 都必须有**——这是 R1 全局必填。包括 archive_message、evidence_record、thesis_note、scenario_note、theme.metadata、portfolio_decision、build artifact 等。
- **吸收的旧 role**：`ingested_at`（archive-first 下 connector 接收 = 写盘是 atomic action，无独立 ingested 时刻）；`built_at`（builder 算 + 写也是 atomic）。三者全部归 `recorded_at`。
- **不可变**：archive-first 强制 once written never updated；后续修改用 `updated_at` 表达。
- **存储**：`_at_utc`。
- **决策面**：D1 currency 终点（与 observed_at 配合算 connector / builder lag）；ledger lineage 排序。

### 3.6 `updated_at`

- **含义**：record 的任何 mutable 字段最近一次被改动的时刻。
- **何时用**：overlay 层 mutable record——thesis_note、scenario_note、theme.metadata、path_observation、theme_report 等。
- **何时不用**：archive 层 immutable record（charter §III 禁止 archive 改写；R4 禁此字段出现于 archive 类 schema）。
- **取代旧 role**：`transitioned_at`——后者语义模糊（"哪次 transition？"）；`updated_at` 更准（任何 mutable field 改动即刷新）。
- **与 ledger 一致性**：charter §VI 要求 state change 写 belief_delta evidence；linter 校 `obj.updated_at_utc ≡ max(belief_delta_evidence.recorded_at_utc where linked_object_id = obj.id)`。drift 视为缺陷。
- **存储**：`_at_utc`。
- **决策面**：D4 sweeper staleness（`now - updated_at > stale_after_days` → freshness=stale）。

### 3.7 `horizon_date`

- **含义**：record 内容覆盖的截止时点（"data through X"）。
- **何时用**：thesis_note 引用数据的 cutoff、research note coverage、报告所基于的 fundamentals as-of。
- **何时不用**：report 发布时点（用 `observed_at` 或 `recorded_at`）；review cadence 时点（用 `scheduled_for_at`）。
- **关键区分**：与 `observed_at`（发布时点）经常 diverge——note 今天发布但只引用 6 个月前的数据 → observed_at 新但 horizon_date 老 → **内容 stale**。
- **存储**：常 `_session_date_market` / `_calendar_day_utc`。
- **决策面**：D1+D2 内容 currency；charter §VII"内容 freshness"维度。

### 3.8 `scheduled_for_at`

- **含义**：前瞻性时点——计划在此时刻 / 之后做某事。
- **何时用**：next review trigger（FOMC 后必查 / earnings 后必查）、review_policy.next_scheduled、cron 触发。
- **何时不用**：cadence-only review（可由 `updated_at + cadence` 推；不需独立字段）；过去事件（用 `observed_at`）。
- **存储**：`_at_utc`。
- **决策面**：D4 事件驱动 review trigger。

---

## 4. Per-class registry（the matrix）

每个 object class 在本 §4 显式声明 9 列三态。**新 class 进仓前必须在此表加行**（R2）。

### 4.1 三态语义

- **REQ**：schema-级必填，缺则 schema validation fail
- **OPT**：允许缺；若给出，须遵守该 role 的 storage suffix 与本 contract 比较规则
- **—**：禁止出现；schema 含此字段视为缺陷，linter raise

### 4.2 Class × Role 矩阵

#### Archive 层（immutable，`updated_at` 一律 —）

| Class | observed_at | period_start_at | period_end_at | effective_at | expiry_date | recorded_at | updated_at | horizon_date | scheduled_for_at |
|---|---|---|---|---|---|---|---|---|---|
| `tick` | REQ | — | — | — | — | REQ | — | — | — |
| `kbar_*` (30m/1h/4h/1d) | — | REQ | REQ | — | — | REQ | — | — | — |
| `fundamentals_snapshot` | — | REQ | REQ | — | — | REQ | — | — | — |
| `fed_statement` | REQ | — | — | OPT | — | REQ | — | REQ | — |
| `fed_speech` | REQ | — | — | — | — | REQ | — | OPT | — |
| `fomc_vote` | REQ | — | — | REQ | — | REQ | — | — | — |
| `fomc_meeting` | OPT | REQ | REQ | — | — | REQ | — | — | — |
| `fed_appointment.term` | — | — | — | REQ | REQ | REQ | — | — | — |
| `research_note` | REQ | — | — | — | — | REQ | — | OPT | — |
| `archive_message` | OPT | — | — | — | — | REQ | — | — | — |
| `source_read_content` | — | — | — | — | — | REQ | — | — | — |
| `image_review` | — | — | — | — | — | REQ | — | OPT | — |
| `freshness_event` | — | — | — | — | — | REQ | — | — | — |
| `perplexity_log` | OPT | — | — | — | — | REQ | — | — | — |

#### Overlay 层（mutable，`updated_at` REQ 或 OPT）

| Class | observed_at | period_start_at | period_end_at | effective_at | expiry_date | recorded_at | updated_at | horizon_date | scheduled_for_at |
|---|---|---|---|---|---|---|---|---|---|
| `path_observation` | REQ | — | — | — | — | REQ | REQ | — | OPT |
| `evidence_record` | OPT | — | — | — | — | REQ | REQ | — | — |
| `thesis_note` | — | — | — | — | — | REQ | REQ | REQ | REQ |
| `scenario_note` | — | — | — | — | — | REQ | REQ | REQ | REQ |
| `theme.metadata` | — | — | — | — | — | REQ | REQ | OPT | REQ |
| `theme_report` | — | OPT | OPT | — | — | REQ | OPT | OPT | — |
| `portfolio_decision` | — | — | — | — | — | REQ | — | — | — |
| `asset_technical_packet` | — | — | — | — | — | REQ | — | — | — |
| `asset_technical_report` | — | — | — | — | — | REQ | — | — | — |
| `writer_package` | — | OPT | OPT | — | — | REQ | — | OPT | — |

### 4.3 嵌套子对象与通配符规则

- **嵌套子对象**（如 `fed_appointment.term`）：用点号路径登记，每层独立矩阵行。父对象与子对象各自满足其行的要求。
- **通配符 class**（如 `kbar_*` 涵盖 30m/1h/4h/1d）：用 `*` 表示 family 共用同一行；如某 timeframe 有特殊需求，单独再加一行（`kbar_1d` 覆盖 `kbar_*`）。
- **未登记 class**：不允许进仓。先在本 §4 加一行，再写 schema。

### 4.4 对 charter 的兑现

| Charter 承诺 | §4 矩阵兑现 |
|---|---|
| §III archive 不可改写 | 每条 archive 类 record 必有 `recorded_at`；archive 类禁 `updated_at`（R4）|
| §IV fail loud | matrix 之外的字段视为 unauthorized，linter raise（R3）|
| §VI evidence 必带 belief_delta | `evidence_record` 行 recorded_at REQ + updated_at REQ（overlay 层 belief-revision artifact，charter §I：Evidence 是一等对象）；belief_delta 内字段由 evidence_record schema 单独管 |
| §VII freshness vs lifecycle 二维 | thesis_note / scenario_note / theme.metadata 行 `updated_at` REQ + `scheduled_for_at` REQ + `horizon_date` REQ |
| §VIII 决策可审计 | portfolio_decision 行 recorded_at REQ；引用的 scenario / evidence 各自满足其行 |

---

## 5. Storage suffix（Axis 2）

5 种存储后缀。

| Suffix | 含义 | Storage type | Example |
|---|---|---|---|
| `_at_utc` | wall-clock instant，UTC ISO 8601 | string `YYYY-MM-DDTHH:MM:SSZ` | `recorded_at_utc: "2026-04-18T07:27:53Z"` |
| `_calendar_day_utc` | 纯 UTC calendar slice；仅用于 24/7 资产 | string `YYYY-MM-DD` | `effective_calendar_day_utc: "2026-04-17"` |
| `_session_date_et` | XNYS ET market session day | string `YYYY-MM-DD` | `effective_session_date_et: "2026-04-17"` |
| `_session_date_ct` | CMES CT trading day | string `YYYY-MM-DD` | `effective_session_date_ct: "2026-04-17"` |
| `_session_date_market`（配 `_market_tz`） | 通用 per-asset session 日，tz 由 sibling field 提供 | string `YYYY-MM-DD` + IANA tz | `effective_session_date_market: "2026-04-17"` + `market_tz: "America/New_York"` |

### 5.1 Role × Storage 组合规则

- **point role**（`observed_at` / `recorded_at` / `updated_at` / `scheduled_for_at`）：默认 `_at_utc`。例外只允许显式列出的情况：`observed_at` 可按 §3.1 date-level observed fallback 写 `_at_utc + observed_precision: "date"`；`recorded_at` / `updated_at` / `scheduled_for_at` 只接受 `_at_utc`。
- **interval role**（`period_start_at` / `period_end_at`）：`_at_utc` 优先（区间起讫精确到 instant）；按 session 对齐时可 `_session_date_*`。
- **date role**（`effective_date` / `expiry_date` / `horizon_date`）：常 `_session_date_market` / `_calendar_day_utc`；不接受 `_at_utc`（语义到点是 over-precision）。
- `effective_at` 与 `effective_date` 是同一 role 的两种 storage 形式：精确到点用 `effective_at_utc`，精确到日用 `effective_session_date_*`。
- **Schema guidance**: any schema that requires a `*_session_date_market` field must also require sibling `market_tz`. `market_tz` is not a tenth timestamp role; it is mandatory metadata that makes the `*_session_date_market` storage interpretable.

---

## 6. Comparison contract

### 6.1 跨 role 比较禁止

任何代码比较两个 timestamp 值时必须：

1. 校验两侧 **same role + same storage**（或经 calendar-aware 函数显式转换）
2. 比较前调用 `src.core.timekeeping.compare.assert_compatible(a, b)`
3. **冲突时 raise** `TimestampSemanticsMismatch`（不 silently 退化为 UNKNOWN）

charter §IV fail-loud 适用。planner / executor 在入口捕获并报告 contract violation，不当 transient miss 处理。

### 6.2 UTC-first 比较

任何 `_at_utc` 比较在 UTC 中进行。不要 `astimezone(ET)` 后用 `timedelta` 比较——DST transition day 会有 1 hour 误差。

### 6.3 DST 处理（axiom T11 §2.5 投影）

DST 把 "tz label → UTC offset" 从常数变成 time function。下列规则强制：

1. **仅 IANA tz 标识符合法**——`ZoneInfo("America/New_York")` / `ZoneInfo("America/Chicago")` / `ZoneInfo("UTC")`。禁止：

   ```python
   # ❌ Forbidden — fixed offset 无法表达 DST tz
   ET = timezone(timedelta(hours=-5))
   ET = pytz.FixedOffset(-300)
   ```

2. **Session open/close 来自 exchange calendar，不是 `datetime.combine`**——所有 "market close UTC for day D" 必须经 `xnys_session_close_at_utc(d)` / `cmes_session_close_at_utc(d)`，正确处理 early close + DST。

3. **"N business days ago" 走 calendar，不用 `timedelta`**——`cal.previous_session(d)` / `cal.sessions_in_range(start, end)`；`timedelta(days=N)` 在 DST transition day 漂移 1 小时。

4. **Hour-level lookback 留在 UTC**——"physical hours ago" 直接用 UTC instants 比较；不要先 `astimezone(ET)` 后 `timedelta(minutes=...)`。

5. **存储留 UTC，tz 标签独立字段**——`*_at_utc` 持久化；"哪个 market session" 用 `session_date_market` (date) + `market_tz` (IANA)。绝不从 offset 反推 tz。

6. **DST 边界 wall-clock 构造**——必须用 `ZoneInfo` + 显式 `fold`：spring-forward gap 用 `fold=0`（`ZoneInfo` 自动 normalize），fall-back overlap 用 `fold=1`（取过渡后那次）。在 call site 注释决策。

### 6.4 Validation hygiene（axiom T11 §2.6 投影）

时间字段守卫必须信任 stdlib parser，只翻译异常成 `TimestampSemanticsMismatch`：

```python
# ✅ Correct
def _assert_iana_tz(tz_name):
    try:
        ZoneInfo(tz_name)
    except (ZoneInfoNotFoundError, ValueError, TypeError) as exc:
        raise TimestampSemanticsMismatch(
            f"{tz_name!r} is not a loadable IANA timezone: {exc}"
        ) from exc

def _assert_iso8601_with_offset(value, *, field_label="value"):
    if not isinstance(value, str):
        raise TimestampSemanticsMismatch(...)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise TimestampSemanticsMismatch(...) from exc
    if parsed.tzinfo is None:
        raise TimestampSemanticsMismatch(f"{field_label}={value!r} parses but has no offset")
```

禁止手写 tz / ISO-8601 blacklist 或 regex（必然 drift `ZoneInfo` / `datetime.fromisoformat`）：

```python
# ❌ Forbidden — re-implements stdlib loader
if name.startswith("+") or name.startswith("-"): raise ...
if "/" not in name and name not in {"UTC"}: raise ...
ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}...")
if not ISO_RE.match(s): raise ...
```

任何时候发现自己写 stdlib parser 已 cover 的语法 blacklist，guard 应退化为"调 parser，翻译异常"。

---

## 7. Source of truth functions

所有 session-date 派生必须经下列之一：

- `src.data_update.session_freshness.equity_last_completed_rth_date(now_utc)`
- `src.data_update.session_freshness.futures_last_completed_session_date(now_utc)`
- `src.core.timekeeping.session_date_for_asset(asset_type, anchor_utc)`（新 wrapper，dispatches to above + UTC for crypto/fx）
- `src.core.timekeeping.data_anchor_from_packet(packet_dict)`（backfill / re-derive 用）

直接 `datetime.now().date()` 或 `bar_start.date()` 在任何参与 freshness / idempotency 决策的代码路径**禁止**。

---

## 8. Anti-patterns

```python
# ❌ Cross-role compare without conversion
if frontmatter.report_date == packet.report_date:
    ...

# ❌ Reconstructing market close locally — silently misanchors on early-close + DST
datetime.combine(packet.session_date_market, time(16, 0), tzinfo=ET)

# ❌ Adding new field without semantic suffix
"report_date": "2026-04-18"           # ✗ 无 role + 无 storage
"meeting_date": "2026-03-19"          # ✗ 无 role + 无 storage
"statement_published_at_utc": "..."   # ✗ 带对象前缀（statement_）

# ❌ Fixed-offset for market tz — silent DST bugs
ET = timezone(timedelta(hours=-5))
"<D>T16:00:00-05:00"

# ❌ "previous session" by timedelta — 跳 weekend / 节假日 / DST
last_trading_day = (now_utc - timedelta(days=1)).date()

# ❌ Hand-rolled tz / ISO-8601 validators
if name.startswith("+"): raise ...
ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T...")

# ❌ Mutating archive layer's recorded_at / adding updated_at
archive_message["recorded_at_utc"] = new_time   # 违反 R4 + charter §III
archive_message["updated_at_utc"] = ...         # archive 类禁 updated_at

# ❌ Drift between obj.updated_at and ledger
obj.updated_at_utc = "2026-04-26T10:00Z"
# 没写对应 belief_delta evidence → linter raise drift
```

---

## 9. Migration

### 9.1 v0.x → v1.0 cutover

- v0.x 期 deprecation window（2026-04-19 → 2026-05-19）下 `report_date` / `generated_at` 等 legacy 别名持续作为 read-only 共存
- v1.0 cutover 后（2026-04-26 起）：
  - 新 schema / 新 code 一律按 9 role + per-class registry 写
  - legacy 别名读 path 保留至 2026-05-19；写 path 立刻停止
  - 2026-05-19 后 reader 也停 legacy 别名；老 artifact 通过 `tradectl backfill --time-semantics-v1` 一次性迁移

### 9.2 charter alignment Phase 0 强制依赖

[`charter_alignment_initiative`](progress/charter_alignment_initiative.md) Phase A 起任何新 schema 字段引入前**必先**在本 contract §4 矩阵添 class 行——以下对象的字段 introduction 阻塞在 §4 登记上：

- `evidence_record`（Phase A 新建）
- `scenario_note`（Phase D 新建）
- `path_observation`（Phase D 新建）
- `freshness_event`（Phase C 新建）
- thesis_note 加 `updated_at_utc` / `horizon_session_date_market` / `scheduled_for_at_utc`（Phase B + C 修订）
- theme.metadata 加 `updated_at_utc` / `scheduled_for_at_utc`（Phase C 修订）

### 9.3 timekeeping 工具化

详见 [`progress/timekeeping_canonicalization_initiative.md`](progress/timekeeping_canonicalization_initiative.md)：

- `src/core/timekeeping/` 模块（roles / storage wrappers / compare / parse / registry / lint）
- `tradectl timeaudit` CLI（schema scan + code scan）
- 旧 builders 迁移按 charter alignment Phase E fail-loud sweep 同步推

### 9.4 Machine Audit Runtime Surfaces

```yaml
runtime_surface_ledger:
  - surface: helper
    projection: runtime_agnostic
    path_or_command: src/data_update/session_freshness.py
    owner: designDoc/the_timestamp_semantic.md
    doc_claim: canonical exchange-calendar helpers for last-completed sessions and session-close UTC anchors.
    sync_obligation: update §6-§7 and tests/test_data_update_session_freshness.py when helper names, inputs, or DST behavior change.
    status: active
  - surface: helper
    projection: runtime_agnostic
    path_or_command: src/core/timekeeping/**
    owner: designDoc/the_timestamp_semantic.md
    doc_claim: executable roles, storage parsing, comparison, registry, and lint enforcement for this contract.
    sync_obligation: update §3-§6 and tests/test_timekeeping.py when roles, storage suffixes, comparison semantics, or exception names change.
    status: active
  - surface: command
    projection: runtime_agnostic
    path_or_command: ./.venv/bin/python -m src.cli.tradectl timeaudit --scan-schemas
    owner: src/tools/timeaudit.py
    doc_claim: schema scan for timestamp field naming and matrix compliance.
    sync_obligation: update this doc, timeaudit help text, and tests/test_timeaudit.py when finding codes or scan flags change.
    status: active
  - surface: command
    projection: runtime_agnostic
    path_or_command: ./.venv/bin/python -m src.cli.tradectl timeaudit --scan-code
    owner: src/tools/timeaudit.py
    doc_claim: code scan for suspicious timestamp/date vocabulary and legacy aliases.
    sync_obligation: update this doc and tests/test_timeaudit.py when code-scan watchlist changes.
    status: active
  - surface: schema
    projection: runtime_agnostic
    path_or_command: data/runtime/schemas/*.json
    owner: per-domain T1 schema owner; timestamp fields yield to this T0 matrix
    doc_claim: all time fields use role + storage naming and obey §4 per-class matrix.
    sync_obligation: schema changes add or update §4 matrix row before code/schema admission.
    status: active
  - surface: command
    projection: runtime_agnostic
    path_or_command: ./.venv/bin/python -m src.cli.tradectl backfill --time-semantics-v1
    owner: proposed timekeeping migration owner
    doc_claim: one-time legacy alias migration after 2026-05-19 read-path cutover.
    sync_obligation: if implemented, update §9.1, migration notes, and backfill tests; if not implemented by cutover, record manual migration procedure.
    status: proposed
verification_hooks:
  - ./.venv/bin/python -m pytest tests/test_timekeeping.py tests/test_timeaudit.py tests/test_data_update_session_freshness.py -q
  - ./.venv/bin/python -m src.cli.tradectl timeaudit --scan-schemas --include data/runtime/schemas
  - ./.venv/bin/python -m src.cli.tradectl timeaudit --scan-code --include src
```

### 9.5 Open Decisions

- Legacy alias read path closes on 2026-05-19; this doc should be reviewed then to remove the migration banner.
- Backfill CLI remains proposed until a concrete `tradectl` command exists or a manual migration path is recorded.
- Every new or changed §4 matrix row must state whether automated schema-validator coverage already exists or is intentionally deferred.

---

## 10. References

- `[Axiom-Timestamp]` [T11 Timestamp Semantics Axiom](../09_soul/axioms/t11_timestamp_semantics_explicit.md)（philosophy 层 source）
- `[T0-Charter]` [Analyst Billie Charter](the_charter.md) §III + §IV + §VI + §VII + §VIII（time 字段服务的承诺）
- `[Initiative-Charter-Alignment]` [Charter Alignment Initiative](progress/charter_alignment_initiative.md) Phase 0 + 各 phase 引出新字段
- `[Initiative-Timekeeping]` [Timekeeping Canonicalization Initiative](progress/timekeeping_canonicalization_initiative.md) 模块 + 工具
- `[Session-Ingestion-Boundary]` [Last Session Truth And Ingestion Boundary](last_session_truth_and_ingestion_boundary.md)（per-instrument session anchors，复用本 contract 的 storage 定义）
- **Schema files**：`data/runtime/schemas/*.json`（由本 contract §4 矩阵驱动）

---

## 11. Changelog

- **v1.0 (2026-04-26)** —— T0 restructure。从 "packet / report 字段命名规范" 升级为 "全 repo 时间字段 authority gate"。引入 §0.1 Authority + R1-R4 四条强制规则；§3 9-role taxonomy（observed_at / period_start_at / period_end_at / effective_at(/_date) / expiry_date / recorded_at / updated_at / horizon_date / scheduled_for_at）；§4 per-class registry 矩阵（class × role 三态：REQ / OPT / —）；§5 5 种 storage suffix。吸收旧 role：`ingested_at` + `built_at` 折入 `recorded_at`；`transitioned_at` 重命名为 `updated_at`（语义更准）；`published_at` 折入 `observed_at`；`acknowledged_at` / `reviewed_at` 删除（boolean / state 字段已承载）。保留 §6 比较契约 + DST 处理 + validation hygiene + §7 source of truth + §8 anti-patterns 全部 v0.x 内容。
- **v0.x (2026-04-19)** —— first written. 触发：`report_date` silent semantic 撞车 bug；定义 5 storage suffix + per-artifact §3.1-§3.5 + DST handling + validation hygiene。

# Archive Library — 跨制品归档库

Status: `Step 0 + Step 1 + Step 2 + Step 3 implemented (2026-04-20). Routine wires complete; new write points must follow the helper.`
Owner: 平台层 / artifact_graph 旁路（不进 graph 强依赖）
First raised: 2026-04-20

## 实现入口（落地后）

- 写入 helper：[`src/core/archive_writer.py`](../../src/core/archive_writer.py)
  - `ARCHIVE_PROFILES` 列出全部已注册节点的归档策略
  - `save_to_archive(canonical_path, body, context, sidecar_payload)` 是唯一对外写入 API
  - `verify_archive()` 返回 archive 不变量检查报告
  - `iter_archive_entries / list_archive / diff_archive_entries` 给 query CLI 用
- 一次性迁移：[`scripts/migrate_to_archive_library.py`](../../scripts/migrate_to_archive_library.py)
  - dry-run：`./.venv/bin/python -m scripts.migrate_to_archive_library --include-adhoc`
  - apply：加 `--apply` 标志
- 校验 CLI：
  - `./.venv/bin/python -m src.cli.tradectl maintenance verify-archive`
  - 等价别名：`./.venv/bin/python -m src.cli.tradectl archive verify`
- 查询 CLI（Step 3）：
  - `./.venv/bin/python -m src.cli.tradectl archive list [--node ...] [--asset ...] [--theme ...] [--ticker ...] [--since YYYY-MM-DD] [--until YYYY-MM-DD] [--limit N] [--json]`
  - `./.venv/bin/python -m src.cli.tradectl archive diff --node <node_id> --from <YYYY-MM-DD> --to <YYYY-MM-DD> [--asset ...] [--theme ...] [--ticker ...] [--json]`
- 已 wire 的写入点（写入会自动落 archive + 更新 symlink）：
  - [`src/writers/service.py`](../../src/writers/service.py)（覆盖 6 种 task_kind：theme_report / market_observation / asset_technical_report / weekly_account_review / portfolio_debate / single_stock_analysis）
  - [`src/tools/draft_asset_technical_reports_with_deepseek.py`](../../src/tools/draft_asset_technical_reports_with_deepseek.py) `_draft_and_write_one_report` 的 fidelity-后覆写也走 helper
  - [`src/tools/build_asset_technical_reports.py`](../../src/tools/build_asset_technical_reports.py) `_write_signal_packet`（每日 packet snapshot 入 archive，per_session_date）
  - [`src/tools/extract_structural_patterns_with_claude.py`](../../src/tools/extract_structural_patterns_with_claude.py) Claude vision 写回 packet 共 7 处（统一 `_persist_packet`）
  - [`src/tools/build_market_observation_package.py`](../../src/tools/build_market_observation_package.py) `current-market.package.md` 写入
  - [`src/tools/draft_market_observation_with_deepseek.py`](../../src/tools/draft_market_observation_with_deepseek.py) `_append_handoff_checklist` 在 service.py 写完后追加 handoff 段也走 helper
  - [`src/tools/build_theme_writer_package.py`](../../src/tools/build_theme_writer_package.py) theme writer package 写入
  - [`src/tools/build_single_stock_analysis_package.py`](../../src/tools/build_single_stock_analysis_package.py) single-stock package 写入
- archive 物理根目录：`data/archive/`（迁移 ledger 在 `data/archive/_migration_ledger.csv`）

> 不在 archive scope 内的写入点（artifact_graph 之外的旧路径）：
> - `data/analysis/decision_packages/` `decisions/` `debate_reports/` `execution_previews/`：本身已带日期+hash 自然分桶，不进 archive 复制；如未来要纳入回测，再补一个 ad-hoc 索引层。
> - `data/research/theme_update_drafts/<theme_id>.{ds,json,docx,pdf}.md`：theme 加工中间产物 / 导出件，不属于 PM-facing 真稿；保持原地。

## 1. 为什么要这层

当前 PM-facing 制品（持仓建议、theme 报告、技术报告、daily recap、single-stock 分析）都遵循 `artifact_graph` 的 **latest singleton** 模式：每次重跑覆盖同一个 canonical path。这对「下游链路读最新」很合适，但对 **历史复盘 / 回测 / 决策审计** 几乎没用 —— 一旦 overwrite，前一稿就消失了。

设计目标：

- **单一真源**：每份制品在物理上只存在一个地方（`data/archive/`）
- 不破坏 `artifact_graph` 的 latest singleton 路径合约（freshness gate / 上下游 dependency 全部不动）→ 用 **相对 symlink** 把 canonical path 指向 archive 中当前最新一份
- 每份 archive 文件路径自带时间锚，按制品类型选不同的归档键，便于人手翻阅与脚本回测
- archive 永远只追加，新文件不影响旧文件；symlink 是唯一的可变指针

**v1（双写）→ v2（symlink，本文档采用）的关键差别**：

| 维度 | v1 双写 | v2 symlink（采用） |
|---|---|---|
| 物理文件数量 | latest + archive 两份 | 仅 archive 一份 |
| 真源 | 双源易偏移 | 单一真源 |
| canonical_path 物理形态 | 真文件 | 相对 symlink |
| 下游 reader 改动 | 0 | 0（透明跟随 symlink） |
| 磁盘占用 | 2× | 1× |
| 写入步骤 | 写 latest + 写 archive | 写 archive + 原子更新 symlink |
| 风险 | 偏移 / 维护重 | git symlink、跨平台需关心（本仓 macOS 单机，可控） |

读者收益（reader gain）：

- PM 能从 `archive/` 重建任意一天的 `current judgment / package admission / trade framing`
- 复盘者能比较「同一资产 4/14 vs 4/20 技术报告」、「同一 theme 3/27 vs 4/20 立场」、「pm_action 4/15 vs pm_action_review 4/17」之间的位移
- 任何回测脚本只需扫 `archive/` 就能重建历史决策序列，而不必从 git 历史里挖被覆盖的旧 markdown

## 2. 归档键模型（关键设计）

不同制品的「同一天能不能多稿」语义不同，归档键必须区分：

| 归档键 | 语义 | 适用制品 | 同 key 写入行为 |
|---|---|---|---|
| `per_build_instant` | (节点, session_date, 写入瞬间 ET) 唯一 | 同一天可多稿（盘中、收盘、复盘版各算一份） | 同一分钟内 overwrite，跨分钟新增 |
| `per_session_date` | (节点, session_date) 唯一；同一 session_date 内重跑覆盖 | 每天最多一稿 | 同 session_date 内 overwrite |
| `per_D_filename` | canonical_path 本身已经带 `<D>`，每天天然新文件 | 已经按日期落盘的制品 | 自动唯一，无需额外旁路 |

判断规则（用作下表第 3 列依据）：

- 一稿决策 / 一稿事实记录 → `per_session_date`
- 同一天会随盘中变化重写 → `per_build_instant`
- canonical_path 已含 `<D>` → `per_D_filename`（直接归档原文件即可，可视为已自然归档）

## 3. 五类制品归档对照表

| # | 制品族 | 当前 canonical_path | 归档键 | archive 路径模板 |
|---|---|---|---|---|
| 1 | `account.snapshot`（持仓快照） | `data/account/snapshots/account_<D>.json` | `per_D_filename` | 已天然归档，无需新文件；`archive/` 只补一份 markdown 摘要（可选） |
| 1 | `portfolio.judgment` | `data/analysis/portfolio_decision/portfolio.judgment.md` | `per_build_instant` | `archive/portfolio/portfolio.judgment_<D>_<HHMMET>.md` |
| 1 | `portfolio.package` | `data/analysis/portfolio_decision/portfolio.package.md` | `per_build_instant` | `archive/portfolio/portfolio.package_<D>_<HHMMET>.md` |
| 1 | `portfolio.pm_action` | `data/analysis/portfolio_decision/pm_action_<D>.md` | `per_D_filename` | 已天然归档；可在 archive 建 symlink 镜像 |
| 1 | `portfolio.pm_action_review` | `data/analysis/portfolio_decision/pm_action_review_<D>.md` | `per_D_filename` | 同上 |
| 3 | `theme.knowledge`（standing 框架） | `data/research/themes/reports/<theme_id>.md` | `per_session_date` | `archive/themes/<theme_id>/<theme_id>_knowledge_<D>.md` |
| 3 | `theme.report.ds`（对外稿） | `data/research/themes/reports/<theme_id>.ds.md` | `per_session_date` | `archive/themes/<theme_id>/<theme_id>_ds_<D>.md` |
| 3 | `theme.owner_decision` / `theme.package` | `data/research/theme_update_drafts/<theme_id>.*` | `per_session_date` | `archive/themes/<theme_id>/<theme_id>_<phase>_<D>.{md,json}` |
| 4 | `signal_packet`（deterministic JSON） | `data/knowledge/asset_technicals/signal_packets/<asset_id>.json` | `per_session_date` | `archive/asset_technicals/<asset_id>/<asset_id>_packet_<D>.json` |
| 4 | `asset_technical_report`（DS 写） | `data/knowledge/asset_technicals/reports/<report_id>.md` | `per_session_date` | `archive/asset_technicals/<asset_id>/<asset_id>_<D>.md` |
| 5 | `current-market.judgment` | `data/analysis/market_observation/current-market.judgment.md` | `per_build_instant` | `archive/market_observation/current-market.judgment_<D>_<HHMMET>.md` |
| 5 | `current-market.package` | `data/analysis/market_observation/current-market.package.md` | `per_build_instant` | `archive/market_observation/current-market.package_<D>_<HHMMET>.md` |
| 5 | `current-market.ds`（recap） | `data/analysis/market_observation/current-market.ds.md` | `per_build_instant` | `archive/market_observation/current-market.ds_<D>_<HHMMET>.md` |
| — | `single_stock.judgment / package / ds` | `data/analysis/single_stock_analysis/<ticker>.*.md` | `per_session_date` | `archive/single_stock/<ticker>/<ticker>_<phase>_<D>.md` |

说明：

- `per_build_instant` 文件名里 ET 用 `HHMM`（不带秒）；同一分钟内重写覆盖，跨分钟保留两份（盘中重写少，分钟粒度足够）
- `per_session_date` 文件名里只带 `<D>`（YYYY-MM-DD）；同 session_date 重跑覆盖，保证「每天最多一稿」
- 子目录策略：technical / theme / single_stock 用「资产或主题二级目录」防止 flat 14k+ 文件；market_observation / portfolio 直接 flat（数量可控）
- single_stock 我加进表里是因为它和 theme / portfolio 同源，应一并归档，但当前讨论焦点在用户提的 5 类

## 4. 写入合约（v2 symlink 模式）

新增一个 helper：`src/core/archive_writer.py`

```python
def save_to_archive(
    *,
    canonical_path: Path,           # latest 路径（最终是相对 symlink 指向 archive）
    body: str | bytes,              # 已经渲染好的最终内容
    node_id: str,                   # 例：current-market.ds
    archive_root: Path,             # 默认 data/archive/
    archive_subdir: str,            # 例：market_observation, asset_technicals/<asset_id>
    archive_key: Literal["per_build_instant", "per_session_date"],
    session_date: str,              # YYYY-MM-DD
    recorded_at_utc: str,              # ISO8601 UTC
    built_at_local_label: str,      # 例："2026-04-20 13:00 ET"，写进 frontmatter
    sidecar_payload: dict | None = None,   # writer.json 等 sidecar 内容
) -> tuple[Path, Path]:
    """Write the only physical copy into `archive/` and atomically point the
    canonical_path symlink at it.

    Returns (canonical_path, archive_path).
    """
```

行为：

1. 把 `body` 注入 / 更新 frontmatter（`session_date_market`、`recorded_at_utc`、`built_at_local`、`archive_path`、`archive_key`）
2. 计算 `archive_path` 按 `archive_key` 规则；`per_session_date` 同 key 直接覆盖；`per_build_instant` 同分钟覆盖、跨分钟新文件
3. 写 `archive_path`（这是唯一的物理文件）
4. 计算 `canonical_path` 到 `archive_path` 的 **相对路径** symlink target
5. 用 `os.replace` 原子替换 `canonical_path`（先写 `<canonical_path>.tmp` symlink，再 rename）
6. （可选）`sidecar_payload` 写入 `<archive_path>.writer.json`；canonical 旁的 sidecar 也是 symlink
7. 返回 `(canonical_path, archive_path)`

不变量：

- `canonical_path` 永远是 symlink，永远不是真文件
- `canonical_path.resolve()` 必须落在 `archive_root` 内
- 旧 archive 文件永远不被改写（除了同 archive_key 的覆盖）
- symlink target 一律用相对路径（跨机器克隆不破）

错误处理：

- 写 archive 失败 → 抛错，symlink 不动
- symlink 替换失败 → 抛错，但 archive 已落盘可手工恢复
- 第一次接入某节点时若 canonical_path 仍是真文件，helper **必须** 走「迁移分支」：先把现有真文件移入 archive，再替换为 symlink；不允许同时存在「真文件 + 同名 symlink」状态

## 5. Frontmatter 强化（两类共有）

所有走 `save_with_archive` 的 markdown 必须带：

- `session_date_market: YYYY-MM-DD`（已有，沿用）
- `recorded_at_utc: 2026-04-20T17:30:00Z`（已有，沿用）
- 新增 `built_at_local: "2026-04-20 13:30 ET"`（人眼可读，archive 文件名的来源字段）
- 新增 `archive_path: data/archive/market_observation/current-market.ds_2026-04-20_1330ET.md`（双向追溯）
- 新增 `archive_key: per_build_instant | per_session_date`（让脚本能判断同制品的 archive 语义）

JSON 制品（如 `signal_packet.json`）放进 packet 顶层同名字段。

## 6. archive 根路径

统一根：`data/archive/`

```text
data/archive/
  market_observation/
    current-market.ds_2026-04-20_1300ET.md
    current-market.ds_2026-04-20_1605ET.md
    current-market.judgment_2026-04-20_1245ET.md
    ...
  asset_technicals/
    etf_qqq/
      etf_qqq_packet_2026-04-17.json
      etf_qqq_packet_2026-04-20.json
      etf_qqq_2026-04-17.md
      etf_qqq_2026-04-20.md
    etf_spy/
      ...
  themes/
    iran-hormuz-escalation/
      iran-hormuz-escalation_knowledge_2026-04-15.md
      iran-hormuz-escalation_ds_2026-04-20.md
      iran-hormuz-escalation_owner_2026-04-20.json
  single_stock/
    orcl/
      orcl_judgment_2026-04-18.md
      orcl_package_2026-04-18.md
      orcl_ds_2026-04-18.md
  portfolio/
    portfolio.judgment_2026-04-20_1430ET.md
    portfolio.package_2026-04-20_1430ET.md
    pm_action_2026-04-20.md          ← 仅 symlink 或 mirror copy；canonical 已带日期
  experiments/
    current-market.with-handoff.ds.md
    current-market.prompt-experiment.ds.md
    ...
```

理由放 `data/archive/` 而不是各自模块下的 `archive/` 子目录：

- 一处即所有制品历史，回测脚本只扫一个根
- 与 `data/research/`（连接器原始档案）形成对照：`data/archive/` 是 **interpretive / decision** 历史，`data/research/` 是 **raw research** 历史
- 模块自己的目录保留 latest singleton，物理隔离很清楚

## 7. 与 `artifact_graph.yaml` 的关系

- **不动现有 node 的 `canonical_path` 字符串**：路径仍是 `data/analysis/market_observation/current-market.ds.md`、`data/knowledge/asset_technicals/reports/<report_id>.md` 等
- 物理形态从「真文件」变为「相对 symlink → archive/...」；freshness gate 读 frontmatter 时会跟随 symlink，行为与之前完全一致
- 下游 reader（`Path.read_text`、`open(...)`、`yaml.safe_load(open(...))`）在 macOS / Linux 上对 symlink 透明，0 改动
- archive 中的旧文件 **不进 graph**：不被 freshness gate 检查、不被 plan / produce 解析、不被任何 must_be_fresh 引用
- Phase 3 可选：增加 ledger 节点 `archive.ledger` 仅做读边路（让 `tradectl history` 等查询命令能解析），但不参与 freshness 决策

→ 0 graph contract 字符串改动；唯一的运行期变化是 canonical path 在磁盘上变成 symlink。

### symlink 必要约束

- target 一律相对路径，例：`current-market.ds.md → ../../archive/market_observation/current-market.ds_2026-04-20_1605ET.md`
- canonical_path 父目录与 archive_root 同属 repo，跨机器 clone 后路径不变
- git 提交 symlink 本身（git 把它存为 mode `120000` blob = 目标路径字符串），diff 友好
- 工具检查（防御性）：`tradectl maintenance verify-archive` 校验所有声明节点的 canonical_path 都是 symlink、且 resolve 落在 `data/archive/` 内

## 8. 命名规则细则

- **session_date** 一律 ISO `YYYY-MM-DD`（字典序自动按时间排）
- **build_instant** 用 ET `HHMM`（如 `1300ET`、`1605ET`），不写秒；不写 timezone 缩写以外的形式
- **节点前缀** 保留：`current-market.ds_`、`portfolio.judgment_`、`<asset_id>_packet_`、`<theme_id>_ds_` —— 一眼能看出 archive 文件属于哪个 graph 节点
- **混合多 phase 的同主题** 用 `_<phase>_<D>` 后缀分（如 `iran-hormuz-escalation_knowledge_2026-04-20.md` vs `_ds_2026-04-20.md` vs `_owner_2026-04-20.json`）
- **per_build_instant 的 ET 时间戳** 在文件名末尾（让同 session_date 的多稿在字典序里相邻）

## 9. 落地拆分（v2 symlink 模式，4 步走）

### Step 0 — 一次性历史迁移脚本（半小时）— **已完成 2026-04-20**

`scripts/migrate_to_archive_library.py`，幂等，可重复跑：

1. 扫描所有当前 latest 真文件（5 类制品的 canonical_path 全集）
2. 解析 frontmatter `session_date_market` / `recorded_at_utc`
3. 用 `archive_writer` 的命名规则计算 `archive_path`，把真文件 `git mv` 进 archive
4. 在原 canonical_path 建相对 symlink 指向新 archive 文件
5. 同时处理 ad-hoc 历史备份：
   - `data/analysis/market_observation/recap_2026-04-15.md` → `data/archive/market_observation/current-market.ds_2026-04-15_unknownET.md`（缺时间戳标 `unknownET`）
   - `data/analysis/market_observation/recap_2026-04-17.md` → `_2026-04-17_unknownET.md`
   - `data/analysis/market_observation/current-market.with-handoff.ds.md` 等实验稿 → `data/archive/experiments/`
   - `data/research/themes/reports/iran-hormuz-escalation.2026-03-27.md` → `data/archive/themes/iran-hormuz-escalation/iran-hormuz-escalation_knowledge_2026-03-27.md`
6. 输出迁移 ledger CSV / JSON，记录 (old_path, new_archive_path, frontmatter_session_date)

### Step 1 — 建 helper + 接所有 service.py 出稿点（半天）— **已完成 2026-04-20**

- 新建 `src/core/archive_writer.py`，实现 `save_to_archive`（symlink 模式）+ `migrate_existing` + `verify_archive`
- 接入 `src/writers/service.py`（中央 writer）→ 一处 wire 即覆盖 6 种 task_kind：`theme_report` / `market_observation` / `asset_technical_report` / `weekly_account_review` / `portfolio_debate` / `single_stock_analysis`
- 接入 `src/tools/draft_asset_technical_reports_with_deepseek.py:499` fidelity-后的最终覆写 → 走同一个 helper，banner 与 frontmatter 持续注入
- 加 `tradectl maintenance verify-archive` 子命令，跑通报告 `ok=183 issues=0`
- 端到端 smoke test 已验证：per_session_date（technical report）同 session 重写覆盖同一 archive；per_build_instant（current-market.ds）不同 HHMM 落不同 archive 文件且 symlink 正确翻新

### Step 2 — 接所有非 writer-service 直写点（半天）— **已完成 2026-04-20**

`writer service` 已经覆盖 6 种 task_kind；本步把工具自身（不经 service.py）的直写点全部接入：

- ✅ `signal_packet` JSON 落盘：`src/tools/build_asset_technical_reports.py:_write_signal_packet` 接入 helper（per_session_date，每日一份 packet snapshot）；`signal_packet.md` 是 derived view 仍走 plain write
- ✅ Claude vision 写回 packet：`src/tools/extract_structural_patterns_with_claude.py` 共 7 处统一 `_persist_packet`
- ✅ `current-market.package.md`：`src/tools/build_market_observation_package.py:317` 接入 helper（per_build_instant）
- ✅ DS recap 追加 handoff 段：`src/tools/draft_market_observation_with_deepseek.py:_append_handoff_checklist` 接入 helper，service.py 写完 archive 后追加段也走同一 archive 文件
- ✅ Theme writer package：`src/tools/build_theme_writer_package.py:372` 接入 helper（per_session_date）
- ✅ Single-stock package：`src/tools/build_single_stock_analysis_package.py:100` 接入 helper（per_session_date）
- ✅ 补 `theme.report.review` profile（artifact_graph 已声明，写入未来到来时即就绪）

不进 archive 的写入点（明确 out of scope）：

- `data/analysis/decision_packages/` `decisions/` `debate_reports/` `execution_previews/`：本身就带日期+hash 自然分桶，不属于 latest singleton 模型；artifact_graph 也未将其作为节点。如未来要纳入回测，再补 ad-hoc 索引层。
- `data/research/theme_update_drafts/<theme_id>.{ds,json,docx,pdf}.md`：theme 加工中间产物 / 导出件，不属于 PM-facing 真稿。
- `current-market.intake.md` / `*.handoff.md`：transient 中间稿，不进 PROFILES。

### Step 3 — query 工具与 verify — **已完成 2026-04-20**

- ✅ `tradectl archive list [--node ...] [--asset ...] [--theme ...] [--ticker ...] [--since ...] [--until ...] [--limit N] [--json]`
- ✅ `tradectl archive diff --node <node_id> --from <D1> --to <D2> [--asset/--theme/--ticker ...] [--json]`：unified diff，per_build_instant 自动取该 session_date 内最新 hhmmet
- ✅ `tradectl archive verify` / `tradectl maintenance verify-archive`：等价别名；最近一次 `ok=183 issues=0 total=183`
- 暂不做自动 retention；archive 永远只追加，磁盘占用可承受（estimate：71 资产 × 365 天 × ~10KB md ≈ 260MB/年；packet json 更小）

## 10. 与现有 doc 的接缝

- `the_artifact_graph.md`：archive 是 graph 的 **旁路**，不动 freshness contract；后续在该文档加一段「archive ledger 不进 graph」的边界说明
- `analysis_platform_and_pm_workspace.md`：补「PM workspace 的 latest singleton + archive 平行结构」一节
- `last_session_truth_and_ingestion_boundary.md`：archive frontmatter 的 `built_at_local` 与 `recorded_at_utc` 沿用本文档定义的 timestamp semantics，不引入新时钟
- `research_10_thematic_workflow.md`：明确区分 `data/research/`（raw research archive）vs `data/archive/`（interpretive decision archive）

## 11. 已确认 / 待拍板

### 已确认（2026-04-20）

1. ✅ **archive 根目录**：统一一根 `data/archive/`
2. ✅ **天然带日期的制品**（`account.snapshot`、`pm_action_<D>`）：不 mirror，沿用原 canonical 路径作为 archive 物理存储；但归类视角下仍属 archive library 的一部分（archive index 列出指针）
3. ✅ **历史 ad-hoc 备份**：一次性 git mv 进 archive，迁移脚本独立审
4. ✅ **真源唯一**：放弃 v1 双写，采用 v2「archive 是真源 + canonical 是 symlink」

### 仍待拍板

A. **天然带日期的制品要不要也建 symlink 到 archive 视图**？例如建一个 `data/archive/account/account_<D>.json` symlink → `data/account/snapshots/account_<D>.json`，这样 `data/archive/` 一处即可看到所有制品的历史。
   - 推荐：建反向 symlink（archive 视图统一），不动原 canonical 路径
   - 拒绝：保持原状，只在 `tradectl history list` 里逻辑聚合

B. **archive 文件 immutable**：是否给写完的 archive 文件加 `chmod -w` 防止 agent 后续误覆盖？
   - 推荐：**不加**，靠合约 + verify 工具检查；便于人工修复打错的归档

C. **`per_build_instant` 同分钟覆盖语义**：30 秒内重写是否新增文件？
   - 推荐：保持分钟粒度，同分钟覆盖；秒粒度只在调试出现，覆盖可接受

D. **prompt / writer.json sidecar 是否一并归档**：
   - 推荐：sidecar 作为 archive 真文件的伴随文件一并落 archive；canonical 旁的 sidecar 也用 symlink；prompt 内容（system prompt + user prompt + token 计数）扩展到 sidecar 字段，便于复现

E. **Cursor IDE 编辑 symlink 的体验**：用户在 IDE 里直接编辑 canonical_path 时，会跟随 symlink 编辑到 archive 真文件。这是预期行为，但意味着 archive 有可能被人工修改 → 是否要在 archive 文件里加 `# AUTO-WRITTEN; edits go through save_to_archive helper.` 顶部注释提醒？
   - 推荐：加注释提醒，但不强制 immutable

## 12. Reader End-State Check

按 `35_pm_reader_state_first.mdc`：读完这份 plan 后，PM / 维护者应该能：

- 说出每类制品归档进哪个目录、用什么键
- 判断同一天能不能多稿、跨天怎么留底
- 知道 archive 不进 graph、不影响 freshness gate
- 区分 `data/archive/`（interpretive）与 `data/research/`（raw research）的归档边界
- 看懂 frontmatter 三个新字段的用途
- 列出 Step 1 / 2 / 3 的实施顺序与每步的 acceptance

如果还回答不出上述任何一条，回到对应章节补足细节再开工。

## 13. Changelog

- 2026-04-20 v1：初稿，双写模式（latest singleton + 平行 archive 副本）；6 个待拍板项。
- 2026-04-20 v2：升级为 symlink 模式（archive 是唯一真源 + canonical 退化成相对 symlink）；落地拆分加 Step 0（一次性迁移脚本）；待拍板项收敛为 5 个（A-E），4 个已确认。
- 2026-04-20 v2.1（implementation）：用户拍板全部 5 个待拍板项采用推荐方案，Step 0 + Step 1 落地：
  - 实现 `src/core/archive_writer.py`（含 14 个 ArchiveProfile、`save_to_archive`、`migrate_existing`、`verify_archive`、`iter_known_canonical_paths`）
  - 实现 `scripts/migrate_to_archive_library.py`（dry-run / apply / include-adhoc，幂等）
  - 一次性迁移：186 个 canonical 路径 + 7 个 ad-hoc 备份，全部移入 `data/archive/` 并建立相对 symlink；ledger 写到 `data/archive/_migration_ledger.csv`
  - Wire `src/writers/service.py` 中央 writer（覆盖 6 种 task_kind）+ `src/tools/draft_asset_technical_reports_with_deepseek.py` fidelity-后覆写
  - 新增 `tradectl maintenance verify-archive` CLI；首跑结果 `ok=183 issues=0 total=183`
  - 端到端 smoke test 验证两类归档键行为正确（per_session_date 覆盖、per_build_instant 增稿）
- 2026-04-20 v2.2（implementation）：Step 2 + Step 3 落地：
  - Step 2 wire 完所有非 service.py 的直写点：
    - `signal_packet` JSON：`build_asset_technical_reports._write_signal_packet` → `save_to_archive`
    - Claude vision 写回 packet：`extract_structural_patterns_with_claude` 7 处统一 `_persist_packet`
    - `current-market.package.md`：`build_market_observation_package`
    - DS recap handoff appendix：`draft_market_observation_with_deepseek._append_handoff_checklist`
    - Theme writer package：`build_theme_writer_package`
    - Single-stock package：`build_single_stock_analysis_package`
    - 补 `theme.report.review` profile（artifact_graph 已声明，写入未来到来时即就绪）
    - 明确 out of scope：`decision_packages/decisions/debate_reports/execution_previews/`（已自带日期+hash）、`*.intake.md`、`*.handoff.md`、theme drafts 中间件
  - Step 3 query CLI：
    - 新增 `iter_archive_entries / list_archive / diff_archive_entries` helper
    - 新增 `tradectl archive list/diff/verify` 子命令；`archive verify` 与 `maintenance verify-archive` 等价
  - smoke test：`signal_packet` 重写不破坏 symlink 且 archive 文件携带 `archive_path/archive_key/banner`；`archive list` 正确按 session_date desc 列出 184 archive 文件；`archive diff` 正确对 current-market.ds 跨 session 出 unified diff
  - verify-archive 仍 `ok=183 issues=0 total=183`

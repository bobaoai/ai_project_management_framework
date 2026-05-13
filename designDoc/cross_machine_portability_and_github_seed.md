# Cross-Machine Portability And GitHub Seed Design

**Version 0.2 — 2026-04-15**

This document updates the repo's migration policy after the first GitHub portability pass.

The key change is no longer only `what should we carry`, but also:

- which files are `authoring truth` and should travel together
- which files are `derived state` and are better rebuilt locally
- which files are only `run-local sidecars / debug artifacts` and should stay out of GitHub

The practical target remains the same:

- GitHub as the fastest portable seed
- enough code, docs, semantic objects, and authored reports for AI to take over on another machine
- secrets, tokens, caches, and machine-local runtime state kept out of GitHub by default

---

## 1. Purpose

当前问题不是“如何立刻做完整云原生重构”，而是：

1. 哪些内容必须跟 repo 一起走，另一台电脑上的 AI 才能继续工作
2. 哪些内容应该成组一起上传，避免带了 report 却没带它的 metadata / draft / source registry
3. 哪些内容已经有稳定的 rebuild path，适合在另一台机器本地重新生成
4. 哪些内容只是本机运行痕迹，不值得进入 GitHub seed

这个文档要让读者在迁移结束后能明确回答：

- `must carry now`
- `carry as one bundle`
- `rebuild locally`
- `exclude by default`

---

## 2. What Changed Since The First Migration Attempt

和 2026-03-27 那次相比，这次 repo 的边界更清楚了，主要有四个变化。

### 2.1 AI Operating Surface Is More First-Class

现在真正决定另一台机器上 AI 能否快速接手的，不只是 `src/` 和 `README.md`，还包括：

- `.cursor/rules/`
- `.cursor/skills/`
- `.cursor/context/update_batches/`
- `09_soul/`
- `designDoc/`

这些内容现在已经是 repo 的正式 operating surface，而不是可有可无的附属说明。

### 2.2 Theme / Thesis / Draft Boundaries Are Clearer

当前 theme 流程已经更明确地区分了：

- canonical theme report
- active theme update draft
- thesis notes
- generated indexes / priority views

因此这次迁移不能再把 `theme metadata + report + draft + index` 混成一个模糊大包。要明确：

- `metadata / reports / drafts / thesis notes` 更接近 authoring truth
- `index.json / current_priority_tree.json / hierarchy_index.json / thesis_index.jsonl` 更接近 rebuildable generated state

### 2.3 Asset Technical Workflow Now Has Clearer Canonical vs Generated Layers

现在 asset technical 路径已经分成三类对象：

- canonical inputs:
  - `profiles/`
  - `profiles.json`
  - `observation_baskets.json`
- current overwrite-only generated runtime:
  - `generated_profiles/`
  - `coverage_index.*`
  - `signal_packets/`
  - `index.*`
- authored output:
  - `reports/*.md`

这意味着本次迁移需要把 `AI-written reports` 和 `generated technical runtime` 分开看待。

### 2.4 Analysis Run Outputs Now Have A Clearer Local-Only Home

当前市场观察的 package / intake / DS 草稿已经更明确地落在：

- `data/analysis/market_observation/`

这类对象反映的是一次 run 的本地工作面，不应再默认当作 GitHub portable seed 的核心组成。

如果其中某个结果值得长期保留，应提升进 canonical semantic layer，而不是直接把整个 `data/analysis/` 当作 must-upload。

---

## 3. Portability Classes

本 repo 里的迁移对象现在应按四类处理。

### 3.1 Class A: Portable Authoring Truth

这些对象应优先上传，因为它们保存的是长期可复用的人类 / AI 判断结果，或者是理解 repo 必需的 operating contract。

典型内容：

- docs / rules / skills / code
- theme metadata
- theme reports
- active theme drafts
- thesis notes
- snapshots
- asset logic cards
- AI-written asset technical reports
- source routing registries

### 3.2 Class B: Deterministic Derived State

这些对象是从 canonical source 可以重新生成的。它们可以上传，但优先级低于 authoring truth；若要压缩 portable seed，优先保留 source，省略 derived output。

典型内容：

- theme indexes
- thesis index
- snapshot index
- asset logic index
- asset technical coverage/index views
- package manifests and assembly manifests

### 3.3 Class C: Rebuildable Runtime Current State

这些对象不是长期 authoring truth，而是当前窗口的 runtime view。它们通常可以在另一台机器重建，但前提是本地 secrets、数据库、broker/provider access、以及必要 cache 已恢复。

典型内容：

- current signal packets
- current market-observation package / intake / DS artifacts
- generated technical profiles
- local watchlist operational state in Postgres

### 3.4 Class D: Machine-Local Or Sensitive State

这些对象默认不上传。

典型内容：

- `.env`
- `token/`
- `data/account/`
- `data/connectors/`
- `data/agents/`
- local logs
- SQLite / parquet / cache
- full raw message archive

---

## 4. Updated GitHub Seed Policy

### 4.1 Repo Privacy Rule

当前仍推荐使用 `private GitHub repository`。

原因不变：

- repo 包含 PM-facing reports
- repo 包含研究判断、主题结构、资产逻辑
- 即使不上传 raw archive，也足以暴露内部工作框架

### 4.2 Bundle A: Repo Operating Intelligence

这是另一台电脑上 AI 能理解 repo 的最小核心，必须成组上传。

- `README.md`
- `AGENTS.md`
- `.cursorrules`
- `.cursor/rules/`
- `.cursor/skills/`
- `.cursor/context/update_batches/latest.md`
- `.cursor/context/update_batches/archive/`
- `09_soul/`
- `designDoc/`
- `src/`
- `tests/`
- `requirements.txt`

这组文件的价值不是“能跑起来”，而是：

- AI 能恢复 operating posture
- AI 能读到当前 routing / skill / layer 边界
- 新机器能理解哪些对象是 canonical，哪些是 generated

### 4.3 Bundle B: Canonical Research And Knowledge Authoring Layer

这是继续 PM 工作最重要的 semantic bundle，应优先带走。

#### Research semantic layer

- `data/research/source_collections.json`
- `data/research/senders.json`
- `data/research/snapshots/`
- `data/research/thesis_notes/`
- `data/research/themes/metadata/`
- `data/research/themes/reports/`
- `data/research/theme_update_drafts/`

#### Knowledge semantic layer

- `data/knowledge/asset_logic_cards/`
- `data/knowledge/asset_technicals/profiles/`
- `data/knowledge/asset_technicals/profiles.json`
- `data/knowledge/asset_technicals/observation_baskets.json`
- `data/knowledge/asset_technicals/reports/`

这组文件是当前 repo 最重要的 `portable semantic dataset`。

### 4.4 Bundle C: Rebuild-Friendly Derived Views

这些文件可以上传，但它们不应比上游 authoring truth 更优先。

- `data/research/themes/index.json`
- `data/research/themes/current_priority_tree.json`
- `data/research/themes/hierarchy_index.json`
- `data/research/snapshots_index.jsonl`
- `data/research/thesis_index.jsonl`
- `data/knowledge/asset_logic_cards/index.jsonl`
- `data/knowledge/asset_technicals/coverage_index.json`
- `data/knowledge/asset_technicals/coverage_index.md`
- `data/knowledge/asset_technicals/index.json`
- `data/knowledge/asset_technicals/index.md`

推荐策略：

- 时间紧时，先保证 Bundle A + Bundle B
- Bundle C 可以保留以加快另一台机器上的 read path
- 但若需要瘦身，应优先删 Bundle C，而不是删 authored reports / notes / drafts

### 4.5 Bundle D: Current Technical Continuity Layer

这一组介于 “可重建” 和 “实际很有用” 之间，需要按目标决定是否一起带走。

- `data/knowledge/asset_technicals/signal_packets/`

如果迁移目标是：

- 让另一台机器立刻看到当前 technical state
- 暂时还没恢复 broker/provider auth
- 希望继续沿着当前 technical read 接着写

那么这组值得一起上传。

如果迁移目标是：

- 另一台机器会先补齐 auth / DB / market-data access
- 之后再本地重建 technical runtime

那么这组可以不作为 must-have。

### 4.6 Optional Evidence Bundle

当某个主题或 thesis 的关键判断强依赖原始来源时，可以选择性带 source evidence，但要成组带，而不是只带单个文件。

对单条 research item，建议一起带：

- `messages/<research_id>/message.json`
- `messages/<research_id>/content.md`
- `messages/<research_id>/summary.json`
- `messages/<research_id>/image_reviews.jsonl` when present
- `messages/<research_id>/links.json` when present

只在真正需要 source recall 时这么做；不要默认把整个 raw archive 推到 GitHub。

---

## 5. What Should Be Uploaded Together

本节直接回答：哪些文件不该拆着传。

### 5.1 Theme Bundle

一个 theme 若要可迁移、可继续维护，最少应一起带：

- `data/research/themes/metadata/<theme_id>.json`
- `data/research/themes/reports/<theme_id>.md`

如果该 theme 正在 review / update 中，还应一起带：

- `data/research/theme_update_drafts/<theme_id>.json`
- `data/research/theme_update_drafts/<theme_id>.ds.md` when present
- `data/research/theme_update_drafts/<theme_id>.package.md` when present

不要只带 report 不带 metadata；也不要只带 draft 不带 canonical report。

### 5.2 Thesis Bundle

每条 thesis 至少应一起带：

- `data/research/thesis_notes/<thesis_id>.json`

如果它高度依赖 snapshot context，建议同时带相关：

- `data/research/snapshots/<snapshot_id>.json`
- `data/research/snapshots/<snapshot_id>.md`

### 5.3 Asset Technical Bundle

若希望另一台机器继续使用当前 technical layer，一个 asset 的最小 bundle 是：

- `data/knowledge/asset_technicals/reports/<report_id>.md`
- `data/knowledge/asset_technicals/signal_packets/<report_id>.json`
- `data/knowledge/asset_technicals/signal_packets/<report_id>.md`

而 asset technical 的全局基础配置应一起带：

- `data/knowledge/asset_technicals/profiles/`
- `data/knowledge/asset_technicals/profiles.json`
- `data/knowledge/asset_technicals/observation_baskets.json`

不要只带 AI-written report 而完全不带方法配置；也不要只带 signal packets 却不带 report，如果你希望保留既有 judgment。

### 5.4 Research Evidence Bundle

若某条 theme / thesis 需要保留 source evidence，不要只带 index 行。应带底层对象本身，然后再视需要重建 index。

### 5.5 Migration Rule

优先打包 `object + its canonical context`，而不是只打包某个方便搜索的 index。

---

## 6. What Can Be Rebuilt Locally On Another Machine

本节直接回答：哪些文件根据当前 repo 已有内容，可以在别处本地再生成。

### 6.1 Rebuild From Uploaded Canonical Files Only

这些对象可以不依赖外部 API，直接从 repo 内 canonical objects 重建：

- `data/research/themes/index.json`
- `data/research/themes/current_priority_tree.json`
- `data/research/themes/hierarchy_index.json`
- `data/research/thesis_index.jsonl`
- `data/research/snapshots_index.jsonl`
- `data/knowledge/asset_logic_cards/index.jsonl`

如果上传了完整 `messages/` subtree，则还能重建：

- `data/research/messages_index.jsonl`
- `data/research/links_index.jsonl`

### 6.2 Rebuild After Local Secrets / Data Access Are Restored

这些对象有 rebuild path，但不只依赖 GitHub 内容：

- `data/knowledge/asset_technicals/generated_profiles/`
- `data/knowledge/asset_technicals/coverage_index.json`
- `data/knowledge/asset_technicals/coverage_index.md`
- `data/knowledge/asset_technicals/signal_packets/`
- `data/knowledge/asset_technicals/index.json`
- `data/knowledge/asset_technicals/index.md`
- Postgres watchlists and related operational tables
- `data/analysis/market_observation/` current run artifacts

它们通常依赖：

- local `.env`
- `token/`
- Postgres
- latest account snapshots
- broker / provider market data

### 6.3 Technically Rewritable But Still Worth Preserving

以下内容虽然“理论上可以再写一遍”，但不建议把它们视作 expendable generated output：

- `data/research/themes/reports/*.md`
- `data/research/theme_update_drafts/*.json`
- `data/research/theme_update_drafts/*.ds.md`
- `data/research/theme_update_drafts/*.package.md`
- `data/research/thesis_notes/*.json`
- `data/research/snapshots/*.json`
- `data/research/snapshots/*.md`
- `data/knowledge/asset_logic_cards/*.json`
- `data/knowledge/asset_technicals/reports/*.md`

原因：

- 它们承载的是已经形成的 judgment，而不是纯派生缓存
- 即使有生成路径，也未必能在另一台机器上稳定复现同样的语义结果
- 从迁移价值看，它们是 first-class portable assets

---

## 7. Updated Default Exclusions

默认不要上传：

- `.env`
- `token/`
- `data/account/`
- `data/connectors/`
- `data/agents/`
- `data/ticks.sqlite`
- `data/hist/`
- parquet history caches
- `data/analysis/`
- `data/knowledge/news/`
- `data/research/messages/` full raw archive unless selectively chosen
- `data/research/messages_index.jsonl` when the underlying `messages/` tree is absent
- `data/research/links_index.jsonl` when the underlying `messages/` tree is absent
- `data/knowledge/asset_technicals/generated_profiles/`
- `*.writer.json`
- `*.package.manifest.json`
- `*.intake.manifest.json`
- local logs and scratch outputs

新增说明：

- `*.writer.json` 是 writer backend / package path sidecar，不是 canonical authored content
- `*.package.manifest.json` 与 `*.intake.manifest.json` 更接近 assembly/debug trace
- `data/analysis/` 是 run-local work surface，不应自动进入 portable seed

---

## 8. Why The Priority Changed

这次迁移判断比上次更细，不是因为方向变了，而是因为 repo 现在已经能区分：

- authored semantic objects
- deterministic derived views
- current runtime state
- sidecars and debug traces

所以现在的 portable priority 应该是：

1. `AI can understand the repo`
2. `AI can continue authored PM/research work`
3. `new machine can rebuild operational and current runtime state`

换句话说：

- 先保住 docs / rules / skills / semantic reports / notes / drafts
- 再考虑 generated indexes 是否一起提交
- 最后才考虑 current runtime outputs 和 raw archives

---

## 9. New-Machine Rebuild Playbook

另一台电脑拿到 portable repo 后，建议按以下顺序恢复。

### 9.1 Clone And Install

```bash
pip install -r requirements.txt
```

### 9.2 Recreate Local Secrets

手工补齐：

- `.env`
- `token/`

至少包括：

- `SCHWAB_CLIENT_ID`
- `SCHWAB_CLIENT_SECRET`
- `SCHWAB_CALLBACK_URL`
- `PLATFORM_DATABASE_URL`
- `PLATFORM_DATABASE_SCHEMA`
- optional provider keys such as `EODHD_API_TOKEN`

### 9.3 Provision PostgreSQL

创建新的 `trading_platform` database，并让本地 `.env` 指向它。

### 9.4 Rebuild Deterministic Indexes First

```bash
python -m src.tools.build_theme_indexes
python -m src.tools.build_thesis_index
python -m src.tools.build_asset_logic_index
```

### 9.5 Rebuild Operational Coordination Layer

```bash
python -m src.cli.tradectl watchlists sync-themes
```

### 9.6 Rebuild Current Technical Runtime Only After Auth And Data Are Ready

当 broker/provider auth、account snapshots、以及 DB 已恢复后，再重建：

```bash
python -m src.tools.build_asset_technical_reports
python -m src.tools.build_asset_technical_index
```

### 9.7 Rebuild Current Analysis Run Outputs Only When Needed

如果需要恢复当前 market-observation 的本地工作面，再运行对应 package / draft builder。

默认不要求把旧机器的 `data/analysis/` 原样搬过去。

---

## 10. Working Rules For Future Migration Decisions

在真正完成云端迁移前，本 repo 应遵守以下便携规则：

1. 新对象先判断它属于 `authoring truth`、`derived state`、`runtime current state` 还是 `machine-local sidecar`。
2. 只有 `authoring truth` 才默认进入 portable GitHub seed。
3. 若一个 generated file 能稳定重建，就不要让它成为唯一真相面。
4. 若一个对象只是本地 run surface，就优先留在 `data/analysis/` 或其他 local-only layer，而不是直接进入 Git。
5. 若一个 index 依赖未上传的底层 archive，就不要把该 index 当作 portable must-have。
6. 若某个 report / draft / note 虽然理论上可以再生成，但实际承载了 judgment，就按 authored asset 处理，不要轻易降级成 cache。

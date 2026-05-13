---
title: Source Family Ingestion Playbook
status: active_draft
reader_persona:
  - System Builder
  - Archive Analyst
  - Analysis Platform Builder
---

# Source Family Ingestion Playbook

## 1. 这份文档负责什么

本文件定义不同上游 source family 的 message ingestion / read policy。

它不替代：

- `ingestion_10_source_connector_contract.md`：connector 边界。
- `ingestion_20_archive_message_contract.md`：archive object 文件结构。
- `ingestion_30_ai_read_content_contract.md`：`read_content.md` 形态。
- `ingestion_40_error_and_blocker_contract.md`：blocker / readiness 行为。

它负责回答：

- 这个 source family 通常长什么样？
- 默认应该 text-led、image-led 还是 hybrid？
- 哪些图片必须进入 `review-images-claude`？
- 哪些图片只保留为 audit，不进入 `read_content.md`？
- 哪些情况由 agent orchestration 决定，其余由 deterministic builder 自动处理？

## 2. 总规则

`source_collection.family` / `collection_id` 驱动本 playbook。

Deterministic code 负责：

- 拉取邮件 / 文件
- 保存 raw artifacts
- 渲染 PDF pages
- 下载 external images
- 写 `image_reviews.jsonl` pending rows
- 写 `read_content.md`

Agent orchestration 负责：

- 判断 source family policy。
- 检查 pending image rows。
- 先 dismiss 明显无判断增量的 pending image rows。
- 选择剩余哪些 pending 图需要 Claude review。
- 跑 `tradectl message review-images-claude`。
- 跑 `tradectl message refresh`。
- 验证 `read_content.md` 是否 ready。

禁止：

- 让 downstream analysis prompt 自己决定读哪几个 archive internals。
  - 无声违反信号：analysis prompt 直接引用 `message.json`、`content.md`、`image_reviews.jsonl` 等 archive internals，而不是只引用 `read_content.md`。
- 对所有 source family 使用同一套 image policy。
  - 无声违反信号：Capital Flows / Citrini / TMTB 的 pending image rows 使用完全相同的 review/skip default，且未读取本 playbook 对应 family section。
- 因为一个 source family prose-heavy 就跳过 PDF / embedded chart 的图片判断。
  - 无声违反信号：source 有 PDF pages / external images，但 `image_reviews.jsonl` 缺失或只有 pending rows，`read_content.md` 却标为 ready 且没有 warning。
- 把已经 `status: reviewed` 的图片纳入常规重跑。
  - 无声违反信号：批量 review 没有按 `status=pending` 过滤，导致已 reviewed rows 的 `reviewed_at` / `review_model` 被无故覆盖。
- 把明显 logo、CTA、avatar、tracking pixel、spacer、decorative footer 送进 image model。
  - 无声违反信号：`image_reviews.jsonl` 中有文件名或尺寸明显属于装饰物的 pending row，却没有先被 local gate dismiss。

## 2.1 Image Review State Logic

`image_reviews.jsonl` 是 `image_reviewed` 判定的 authority。

Batch processing order:

1. Load current `image_reviews.jsonl`.
2. Ignore rows already in terminal `status: reviewed`; do not rerun them in normal batch work.
3. For remaining pending rows, run deterministic prefilter first.
4. Dismiss obvious non-evidence rows as reviewed with `has_visual_evidence=false`, `evidence_value=none`, and a local-gate `review_model`.
5. Send only still-pending evidence-bearing rows to `tradectl message review-images-claude`.
6. Run `tradectl message refresh --force` after row states change so `read_content.md` frontmatter reflects the current ledger.

`read_content.md` computes `image_reviewed` from the current ledger:

- no image review rows: `true`
- every row terminal reviewed, including deterministic dismissals: `true`
- any row still pending / failed / parse-failed: `false`

`read_content.md` frontmatter is a projection. Before producing `agent_evidence.json`, the workflow must check the current ledger again; stale frontmatter cannot override pending rows.

## 2.2 Source Identity Normalization

`source_collection` classification must normalize source identity before applying family policy.

Required normalization:

- Treat email headers as case-insensitive. For example, `X-Mailgun-Variables` and `x-mailgun-variables` are the same field.
- Parse provider variables such as Mailgun `category` and `subdomain` from normalized headers before rule scoring.
- Treat plus-addressed sender variants as the same publication identity when matching an explicit canonical sender. For example, `conkstack+chat-logs@substack.com` should match the registry sender `conkstack@substack.com`.
- Keep the raw sender in `message.json` and `read_content.md`; normalization is for classification, not source rewriting.

This prevents one publication from splitting across multiple source families only because the transport layer used a route-specific address. Detection signal: a known publication appears in `messages_index.jsonl` with `metadata.source_collection.collection_id=unknown` even though its sender domain, Mailgun subdomain, or list identity clearly matches a registered family.

Per-family section 使用固定 slot：

```text
Identifiers
Expected shape
Default read mode
Image policy — must review
Image policy — usually skip
Reader-gain requirement
Operational path
```

## 3. Capital Flows

Identifiers:

```yaml
family: capitalflows
collection_ids: [capitalflows_rates_fx]
```

Expected shape:

- Substack / newsletter email。
- Embedded charts and Bloomberg / TradingView screenshots。
- Rates、FX、inflation swaps、real yields、economic calendars、cross-asset overlays。
- 正文通常给出机制解释，图片经常承载数据证据。

Default read mode:

```yaml
primary: hybrid
fallback_to: text_led
fallback_when: no embedded chart/table/dashboard evidence is present
```

Image policy:

必须 review：

- STIR / SOFR / Fed funds futures charts。
- yield curve / real yield curve / inflation swap dashboards。
- economic calendar tables，尤其 survey vs prior / actual。
- cross-asset overlay charts，如 ES vs SOFR、MOVE vs crude。
- oil / gold / FX / DXY / bond futures charts when used to support macro transmission。

通常跳过：

- video thumbnail。
- author/avatar image。
- Substack publish button。
- logo / CTA / UI decoration。
- pure disclosure / legal footer.

Reader-gain requirement:

每个 high / medium evidence chart 都要说明读者看完后能更好判断什么。例如：

- cuts priced vs cuts removed
- survey vs realized data
- curve repricing vs spot policy move
- front-end inflation bump vs long-run inflation regime shift
- risk-asset resilience vs rates repricing pressure

Operational path:

```bash
./.venv/bin/python -m src.cli.tradectl message review-images-claude --research-id <rid> --image-id <selected_image_id>
./.venv/bin/python -m src.cli.tradectl message refresh --research-id <rid> --force
```

`message refresh` 只重建 canonical `read_content.md`。只有进入 snapshot / thesis / theme promotion 等 research 派生任务时，才显式运行 `message derive-agent-evidence` 来重建 `agent_evidence.json`。

## 4. Citrini

Identifiers:

```yaml
family: citrini
collection_ids: [citrini_research]
```

Expected shape:

- Long-form PDF / memo / field-trip report / deck-like research.
- Prose-heavy, but charts and page images often contain decisive evidence.
- Some reports include many pages where only a minority are real visual evidence.

Default read mode:

```yaml
primary: text_led
fallback_to: hybrid
fallback_when: PDF / report contains charts, tables, diagrams, or infographics
```

Image policy:

即使 prose 为主，PDF page 图、embedded chart、table、diagram、infographic 必须本地渲染并通过 image gate；reviewed 视觉证据只在改变解读时进入 `read_content.md`。

必须 render / preserve：

- PDF pages.
- embedded images.
- charts / tables / diagrams / infographics.

必须 review：

- Charts and tables with numbers or market levels.
- Field-trip visuals that support mechanism claims.
- diagrams explaining supply chain / infrastructure / capability stack.
- pages where OCR/text extraction is poor and image is the only reliable surface.

通常跳过：

- cover.
- disclosure / legal / subscription pages.
- logo / author photo.
- pure text page when text extraction is clean.

PDF page review order:

1. Render page images for audit and replay.
2. Use deterministic PDF layout analysis to find significant visual blocks.
3. Dismiss tiny visual blocks locally when their bbox / crop size is too small to carry chart, table, map, or diagram evidence.
4. Crop the remaining visual region and store it as `review_input_path` on the original `image_reviews.jsonl` row.
5. Use a lightweight crop triage pass to dismiss product photos, decorative images, pure text, cover, TOC, disclosure, or appendix pages with no incremental visual evidence.
6. Send only data-bearing chart / table / map / diagram crops to the no-fallback Claude Opus image review path.

Resolution policy:

- For true data figures, prefer original PDF render scale crops instead of downsampling. The main budget saving should come from cropping to the relevant visual block, not from reducing resolution.
- Downsample only when quota or payload constraints make it necessary; record the downsample policy in `review_input_policy`.
- Do not use PNG/JPEG file size alone as a skip signal. Sparse line charts can be small on disk while still carrying important data.

Reader-gain requirement:

读者应能区分 prose 已经足够支撑的机制判断，和必须依赖 chart / table / diagram 才能确认的证据。图像 review 的主要价值是防止 prose-heavy report 漏掉真正的数据表、field-trip evidence 或 capability-stack diagram。

Operational path:

```bash
./.venv/bin/python -m src.cli.tradectl message review-images-claude --research-id <rid> --image-id <selected_image_id>
./.venv/bin/python -m src.cli.tradectl message refresh --research-id <rid> --force
```

## 5. TMT Breakout / TMTB

Identifiers:

```yaml
family: tmt_breakout
collection_ids: []
```

Expected shape:

- Newsletter / earnings wrap / Slack AMA recap.
- Often text-led with occasional company charts, app metrics, valuation visuals, or screenshots.

Default read mode:

```yaml
primary: text_led
fallback_to: hybrid
fallback_when: embedded KPI / chart evidence exists
```

Image policy:

必须 review：

- Earnings tables.
- Segment KPI charts.
- App data / Apptopia-like charts.
- Valuation or positioning charts.
- Screenshots that show explicit product / traffic / metric evidence.

通常跳过：

- profile images.
- social embeds without data.
- CTA / subscribe buttons.
- generic media thumbnails.

Reader-gain requirement:

The reader should understand what the visual helps distinguish:

- one-off company color vs reusable demand signal
- narrative claim vs data-backed KPI
- valuation pressure vs fundamentals pressure
- product-cycle evidence vs social-media noise

Operational path:

```bash
./.venv/bin/python -m src.cli.tradectl message review-images-claude --research-id <rid> --image-id <selected_image_id>
./.venv/bin/python -m src.cli.tradectl message refresh --research-id <rid> --force
```

## 6. Citrindex Snapshots / Portfolio Updates

Identifiers:

```yaml
family: citrindex
collection_ids: []
```

Expected shape:

- EOD performance snapshot.
- Basket / portfolio update.
- Often compact tables or dashboard-like content.

Default read mode:

```yaml
primary: text_led
fallback_to: hybrid
fallback_when: image rows carry basket / performance / allocation numbers not already in text
```

Image policy:

Review only when image carries actual basket / performance / allocation numbers not already in text.

通常跳过:

- dashboard link buttons.
- repeated footer / CTA.
- logo / branding.

Reader-gain requirement:

读者应能区分 basket performance / allocation data 与 dashboard decoration。图像 review 只在图片补充了正文没有覆盖的数字时增加判断价值。

Operational path:

```bash
./.venv/bin/python -m src.cli.tradectl message review-images-claude --research-id <rid> --image-id <selected_image_id>
./.venv/bin/python -m src.cli.tradectl message refresh --research-id <rid> --force
```

## 7. Conks

Identifiers:

```yaml
family: conks
collection_ids: [conks_index, conks_money_markets]
```

Expected shape:

- Substack / newsletter email focused on money markets, funding plumbing, repo, reserves, RRP, TGA, SOFR, rates spreads, and Fed balance sheet mechanics.
- `conks_money_markets` posts include `Money Market Update`, `Plumbing Notes`, `Infographics`, and related long-form / chart-bearing research.
- `conks_index` rows are chat-thread or thread-notice mail; they are usually routing/index artifacts rather than full source reads.
- Infographic posts and plumbing notes often rely on charts, tables, or annotated screenshots for the actual mechanism evidence.

Default read mode:

```yaml
primary: hybrid
fallback_to: text_led
fallback_when: the post is a thread/index notice or no data-bearing visual evidence is present
```

Image policy:

必须 review：

- repo / funding-market diagrams and flow charts.
- RRP, TGA, reserve, SOFR, Fed funds, bill, and Treasury curve charts.
- money-market tables or dashboard screenshots.
- infographics that explain plumbing mechanisms or balance-sheet channels.
- visual evidence supporting claims about reserve scarcity, liquidity compression/expansion, or policy plumbing.

通常跳过：

- Substack thread UI chrome.
- author/avatar image.
- publish / subscribe / payment / receipt buttons.
- repeated footer / CTA / legal decoration.
- chat-thread notification decoration without data evidence.

Reader-gain requirement:

The reader should be able to tell what the visual adds to the source:

- reserve / RRP / TGA mechanics vs newsletter prose assertion
- funding stress signal vs normal plumbing noise
- balance-sheet channel vs rates-market price action
- repo or bill-market mechanism vs generic liquidity language

Operational path:

```bash
./.venv/bin/python -m src.cli.tradectl message review-images-claude --research-id <rid> --image-id <selected_image_id>
./.venv/bin/python -m src.cli.tradectl message refresh --research-id <rid> --force
```

For `conks_index`, first decide whether the row is only a thread notice. If it is only a wrapper / notice, preserve provenance but do not promote it as a full source read unless the body contains unique source content.

## 8. Generic Substack / Newsletter

Identifiers:

```yaml
family: unknown | generic_newsletter | substack
collection_ids: []
```

Expected shape:

- Text-led newsletter by default.
- Embedded images vary by sender and require local inspection.

Default read mode:

```yaml
primary: text_led
fallback_to: hybrid
fallback_when: embedded image is data-bearing
```

Image policy:

Run agent inspection first. Escalate to Claude image review only when the image is data-bearing:

- chart
- table
- dashboard
- screenshot with explicit evidence
- infographic / diagram

社交图片或 CTA 默认保持 audit-only，除非其中包含明确数据证据。

Reader-gain requirement:

Generic family 的 reader gain 只能在 evidence-bearing visual 出现后定义；如果 source family 反复出现同类视觉证据，应新增专属 family section。

Operational path:

```bash
./.venv/bin/python -m src.cli.tradectl message review-images-claude --research-id <rid> --image-id <selected_image_id>
./.venv/bin/python -m src.cli.tradectl message refresh --research-id <rid> --force
```

当 `source_collection.family` 不在本 playbook 已枚举列表里时，按本节 generic policy 处理，并在 verification 阶段保留 warning：该 family 需要补专属 section。

## 9. Verification Checklist

For each newly ingested message:

1. Identify `source_collection.family` / `collection_id`.
2. Read this playbook section for that family.
3. Confirm raw archive surfaces exist.
4. Inspect `image_reviews.jsonl` pending rows.
5. Decide which rows require Claude review.
6. Run:

```bash
./.venv/bin/python -m src.cli.tradectl message review-images-claude --research-id <rid> --image-id <selected_image_id>
```

Canonical Claude image-review prompt shape:

- keep the fixed instructions first and byte-stable across images
- put dynamic fields such as `image_id` and `image_path` at the end of the prompt
- keep CLI flags stable: `--model claude-opus-4-7`, `--effort max`, `--output-format json`
- do not use `--permission-mode bypassPermissions`
- record Claude Code outer `usage` into `image_review_usage.jsonl` so cache behavior is observable

The production path remains one image per Claude call. Do not batch multiple images into one prompt unless the quality contract is explicitly revalidated.

7. Run:

```bash
./.venv/bin/python -m src.cli.tradectl message refresh --research-id <rid> --force
```

8. Open `read_content.md` and verify:

- `readiness_status` is `ready` or explicitly blocked.
- Reviewed visual evidence appears when it changes interpretation.
- Decorative / non-evidence images do not pollute `read_content.md`.
- `upstream_blockers[]` and `warnings[]` are honest.

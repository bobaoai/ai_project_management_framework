---
title: Canonical Source Read Content Contract
status: active_draft
reader_persona:
  - System Builder
  - Archive Analyst
  - Analysis Platform Builder
---

# Canonical Source Read Content Contract

## 1. 这份文档负责什么

本文件定义下游 AI agent 默认读取的一份 canonical source surface。

`read_content.md` 的意思是“给 AI 读取的 source content”，不是“AI 读完以后生成的解释结果”。AI 读完该 source surface 后产生的派生证据属于 `agent_evidence.json`，由 `tradectl message derive-agent-evidence` 显式生成。

核心规则：

```text
下游 AI 默认只读 read_content.md
```

Archive 可以继续保留多文件结构，但下游 task prompt 不应列出一串 archive internals，让 agent 自己判断哪个是正文、哪个是图片证据、哪个是派生摘要。

## 2. Canonical path

默认路径：

```text
data/research/messages/<research_id>/read_content.md
```

如果未来确实需要任务特定版本，可以扩展：

```text
data/research/messages/<research_id>/read_content/<task_surface>.md
```

但默认先使用单一 `read_content.md`。不要过早为每个 skill 创建不同 content 版本。

## 3. Reader end-state

下游 AI 读完 `read_content.md` 后，应该能够：

- 理解 source 在讲什么
- 看到必要 source metadata
- 读到清洗后的正文
- 读到已经嵌入正文位置的 reviewed image evidence
- 知道哪些内容被省略或不确定
- 知道上游是否存在 blocker
- 在需要审计时知道可以打开哪些 `audit_paths[]`

如果 agent 还必须再打开 `content.txt`、`content.md`、`image_reviews.jsonl`、`agent_evidence.json` 才能完整理解 source，`read_content.md` 就没有完成职责。

## 4. File shape

推荐形态：

```markdown
---
source_research_id: <research_id>
content_type: source_read_content
schema_version: 0.1
content_mode: text_led|image_led|hybrid
readiness_status: ready|ready_with_warnings|blocked|partial_needs_selection|failed
recorded_at_utc: <ISO-8601 UTC instant>
source_collection: <source_collection>
image_reviewed: true|false
upstream_blockers: []
warnings: []
omitted_surfaces: []
audit_paths: []
---

# Source Card

<必要 source metadata>

# Canonical Read Content

<清洗后的正文。reviewed image evidence 应嵌入到相关段落附近。>

# Omitted Or Uncertain Material

<仅在有必要时出现。>
```

Frontmatter 是下游 stop / audit / provenance 的机器可读入口。正文是下游 agent 真正阅读的材料。

`image_reviewed` 的 authority 是当前 `image_reviews.jsonl` ledger，不是旧的 `read_content.md` frontmatter。Frontmatter 只是 builder 在写 `read_content.md` 时投影出来的状态。

判定规则：

- `image_reviews.jsonl` 不存在或没有 rows：`image_reviewed=true`，表示当前 archive 没有图片 review 债务。
- 所有 rows 都到达 terminal reviewed state：`image_reviewed=true`。这包括真实视觉证据已被模型 review，也包括明显无判断增量图片已被 deterministic prefilter dismiss 成 reviewed row。
- 任意 row 仍是 `pending`、`failed`、`parse_failed`、或其他非 terminal reviewed state：`image_reviewed=false`。

`image_reviewed=false` 表示 archive 里仍有图片 review row 未完成。此时 `read_content.md` 可以作为临时 text-led surface 存在，但 message ingestion 还未结束，不能进入 `message derive-agent-evidence` 的可复用证据生成；完成 image review / dismissal 并重新刷新 `read_content.md` 后，所有图片 row 已 reviewed 才能变为 `image_reviewed=true`。

`image_reviewed=true` 不表示每张图片都有 PM 价值。它只表示每个 image row 都已经到达终态：有视觉证据的图片已被 review；明显 logo、CTA、avatar、tracking pixel、spacer、decorative footer 等无判断增量图片已被 deterministic prefilter dismiss，并以 `has_visual_evidence=false` / `evidence_value=none` 的 reviewed row 留在 audit 层。下游只消费有判断增量的 reviewed visual evidence。

## 5. Content builder responsibilities

`read_content.md` builder 负责把 archive internals 收束成一份可读材料。

Builder 应决定：

- 哪个文本 surface 是 canonical body
- 是否需要段落级 cleanup
- 是否存在明显重复 raw-data block
- 哪些 reviewed image evidence 需要嵌入正文
- 哪些 legacy / audit sidecars 只应进入 `audit_paths[]`，而不能进入正文或摘要
- 哪些 page-level references 有助于引用或审计
- 哪些 surface 被省略，以及为什么
- 是否存在 upstream blocker

这些判断属于上游 content assembly，不属于下游 AI prompt。

## 6. Light cleanup contract

轻量清洗是 `read_content.md` 的职责之一。

允许做：

- 把明显的一词一行 / 碎行抽取错误压回可读段落。
- 删除完全不可见 filler / 控制字符。
- 修复显而易见的空行、断句、表格标题漂移。
- 把 PDF OCR 中可恢复的段落顺序整理成自然阅读顺序。

必须保留：

- 数字
- quote
- table label
- chart caption
- page reference
- source title / author / publisher
- 能改变解释的 warning、footnote、disclaimer

禁止做：

- 改写 source 的观点
- 把 uncertain claim 写成确定事实
- 删除看似重复但可能代表不同时间点 / 不同表格行 / 不同 chart series 的内容
- 为了好读而省略关键反例或风险段落
- 删除广告、CTA、newsletter footer、preview text、免责声明、postscript 等“看起来多余”的正文。除非它是纯不可见 filler 或技术性控制字符，否则应保留在正文里。

若 cleanup 有不确定性，不要删除。最多在 frontmatter `warnings[]` 中写 `possible_source_chrome_preserved` 这类提示，告诉 downstream 正文可能含有 source chrome、广告、CTA、tracking residue 或 footer，但这些材料被保留以避免误删 source content。

## 7. Image evidence embedding

图片信息不应作为单独文件交给下游 AI 再二次拼装。

Builder 应从 `image_reviews.jsonl` / reviewed `image_reads.jsonl` 中取出有用的 visual evidence，并嵌入 `# Canonical Read Content` 的相关位置。

推荐写法：

```markdown
## <source section heading>

<正文段落>

<image id="<image_id>">
- Takeaway: <chart/table/diagram 的 main_takeaway>
- Key Numbers: <关键数字，若有>
- Visible Facts: <关键可见事实，若有>
- Interpretation: <reviewed interpretation，若有>
</image>

<后续正文段落>
```

规则：

- 只嵌入真实 visual evidence。封面、logo、纯文字页、页眉页脚不应伪装成 image evidence。
- 正文 inline image block 只保留 `image_id` 和判断所需信息，不显示 `image_path`、`Placement`、下载 URL、文件名等 audit 信息；这些只应出现在 fallback / audit 区。
- 图片 evidence 应跟正文上下文靠近，而不是集中堆在文件末尾；如果有 `image_placements.jsonl` / HTML anchor，builder 应优先按原文位置插入；如果有 `page_texts.jsonl` / `page_number` / `image_path` 页码线索，builder 应按页插入。
- 如果 reviewed visual evidence 暂时无法定位到具体页或段落，可以留在 fallback `Reviewed Image Evidence` 区，但这应是可审计的降级状态，不是默认目标。
- 对从邮件下载的 HTML / newsletter source，如果存在多张有判断增量的 reviewed visual evidence，但 `image_placements.jsonl` 没有找到可匹配的正文 anchor，builder 应写入 `email_image_anchors_missing` blocker；下游必须停止，让 ingestion/source-family agent 回到 archive internals 检查 `body.html`、`external_images.jsonl`、`image_reviews.jsonl` 与 `image_placements.jsonl`。
- 对 logo、CTA、头像、装饰图、纯页眉页脚等无判断增量的图片，builder 不应插入正文，也不应放入 visual evidence 区；只在 `Non-Informative Images` / audit note 中保留一行说明，例如 `image_3: no material visual evidence`。
- 如果 source 是 `image_led`，正文可以由 source card + reviewed visual evidence 主导，`canonical body` 不必硬凑 OCR 长文。
- 如果图片 review 失败且图片是理解 source 所必需，`upstream_blockers[]` 应非空。

## 8. Agent Evidence Boundary

`agent_evidence.json` 是 archive / research promotion 的结构化派生层，不是下游默认读取文件。它由显式 AI agent 读取 `read_content.md` 后生成，包含 `document_read`、`image_reads` 和 `evidence_units`。

`read_content.md` 不消费 `agent_evidence.json`，也不嵌入 `evidence_units` 摘要。数据流必须保持单向：

```text
archive internals -> message refresh -> read_content.md -> message derive-agent-evidence -> agent_evidence.json
```

如果 writer package 或 snapshot / thesis / theme promotion 需要 AI-derived evidence，它们应直接读取 `agent_evidence.json`，并把它作为 research-promotion surface 标注，而不是把这些解释结果回填到 canonical source surface。

## 9. Large research docs

大体积 research doc 可以例外处理，但例外必须显式。

如果单份完整 `read_content.md` 会超过下游可消费范围，builder 应：

- 在 frontmatter 标记 `readiness_status: blocked` 或 `readiness_status: partial_needs_selection`
- 写入 `upstream_blockers[]` 或 `omitted_surfaces[]`
- 给出 chunk / section plan
- 明确哪些部分已经进入当前 content
- 明确下游是否可以继续，还是必须先做上游压缩 / section selection

不要把体积问题转嫁成下游 prompt 的“你自己挑哪些文件读”。

## 10. Downstream consumer contract

下游 prompt 应只需要写：

```text
Read this content file:
data/research/messages/<research_id>/read_content.md

If upstream_blockers[] is non-empty, stop and report the blocker.
Do not open archive internals unless audit_paths[] explicitly points to them.
```

下游不默认读取：

- `message.json`
- `content.txt`
- `content.md`
- `page_texts.jsonl`
- `image_placements.jsonl`
- `agent_evidence.json`
- `image_reads.jsonl`
- `image_reviews.jsonl`

## 11. Readiness checks

`read_content.md` 生成后至少应满足：

- frontmatter 可解析
- `source_research_id` 存在
- `content_type: source_read_content`
- `recorded_at_utc` 存在且为带时区时间
- `content_mode` 存在
- `readiness_status` 存在
- `upstream_blockers[]` 存在
- `warnings[]` 存在
- 正文非空，除非 `readiness_status: blocked|failed`
- 若 `content_mode: image_led|hybrid`，正文中应出现嵌入的 reviewed visual evidence，或 blocker 说明为什么没有
- 若发生 cleanup，正文或 metadata 记录 cleanup / omission

## 12. 与相邻文档的关系

- `ingestion_20_archive_message_contract.md`：定义 builder 可消费的 archive internals。
- `ingestion_40_error_and_blocker_contract.md`：定义 `upstream_blockers[]` 的状态和处理。
- `research_00_writer_package_contract.md`：定义 writer-facing package。它可以消费 `read_content.md`，但两者不是同一个 artifact。
- `research_10_thematic_workflow.md`：定义 read content 之后如何进入 snapshot / thesis / theme promotion。

## 13. Source-Family Image Policy

`source_collection.family` 不能作为跳过图片判断的理由。

对于 Citrini / Capital Flows / TMTB 这类 PDF、newsletter、embedded-image source：

- 如果 source 包含 PDF 或 external images，archive 层必须保留 rendered page images / downloaded image files。
- 图片先进入 `image_reviews.jsonl`，状态可以是 `pending`。
- 在调用 image model 之前，先做 deterministic prefilter：明显 logo、CTA、avatar、button、tracking pixel、spacer、decorative footer、重复 legal/disclosure decoration 直接 dismiss 成 terminal reviewed row，`has_visual_evidence=false`、`evidence_value=none`，不送模型。
- 已经 `status: reviewed` 的图片不重跑；常规批处理只处理 `status: pending` 且 prefilter 后仍可能有 evidence-bearing 内容的 rows。模型提交前和写回前都必须重新读取当前 `image_reviews.jsonl`，防止另一个 worker 已经把同一张图写成 reviewed 后，旧的 pending snapshot 又重复调用模型或覆盖 ledger。
- 只有 `reviewed` 且 `has_visual_evidence=true` 的图像内容进入 `read_content.md` 的 Reviewed Image Evidence。
- 没有 reviewed image evidence 时，`read_content.md` 可以保持 text-led，但必须保留 pending image review 的 warning 或 audit path。
- `message fetch-agentmail` 必须推进到 archive + deterministic `read_content.md` refresh；这个步骤不跑 image review，也不跑 `agent_evidence.json`，所以不提供跳过开关。若 source 带图片，初始 `read_content.md` 应保留 `image_reviewed=false`，直到 `message review-images-claude` 完成后刷新为 true。
- `message refresh` 只重建 canonical `read_content.md` 相关 deterministic surfaces，不调用 `ResearchSummarizer`，不生成 `agent_evidence.json`，不触发 Cursor / OpenAI text fallback。
- `message refresh` 不调用 Cursor / OpenAI image reader；图像 review 的唯一正式入口是 `tradectl message review-images-claude`。
- `message derive-agent-evidence` 是显式 research-promotion 派生入口，用于让 AI agent 读取 `read_content.md` 并重建 `agent_evidence.json`；它不属于默认 ingestion refresh。它必须先检查当前 `image_reviews.jsonl` ledger，而不是只相信旧 `read_content.md` frontmatter。如果当前 ledger 仍未完成，必须阻断；如果现有 `agent_evidence.json` 是基于 `image_reviewed=false` 或未知 image state 生成的，而当前 ledger 已完成，必须覆盖重建，不能复用旧结果。

Runtime anchor:

- `src/message_process/content_surfaces.py`：message 正文清洗、archive `content.md` 渲染、chunk、effective surface 选择、`ResearchItem` 组装兼容逻辑。
- `src/message_process/html_image_placement.py`：从 HTML source body 回填 external image 的 inline anchor。
- `src/message_process/read_content.py`：当前 `read_content.md` 组装逻辑。
- `src/message_process/service.py`：message-level canonical read-content refresh，以及显式 AI-derived read pipeline owner；默认 `message refresh` 只能进入前者。
- `src/message_process/claude_image_review.py`：Claude Code CLI `claude-opus-4-7 --effort max` image review path，无 fallback。
- `src/message_process/archive_store.py`：负责 `messages/<research_id>/` filesystem IO、`read_content.md` 写入、`messages_index.jsonl` 路径 / hash。`write_read_content()` 写入后必须同步 upsert 对应 `messages_index.jsonl` / `links_index.jsonl` row；外部程序绕开 canonical writer 直接落文件后，必须运行 `tradectl message rebuild-index`。
- `src/research/archive.py`：保留 research-level store facade，组合 message store 与 snapshot / thesis / theme stores。

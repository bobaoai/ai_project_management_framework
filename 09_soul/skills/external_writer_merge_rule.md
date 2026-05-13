# External Writer Merge Rule

## 元数据

- **类型**: BestPractice / Caller-side Review Rule
- **适用场景**: main agent / reviewer 合并 Claude、Cursor、DeepSeek、OpenAI 等 external writer drafts 到 canonical artifact
- **创建日期**: 2026-05-04
- **进入 worker stable prefix**: 否。除非任务明确要求 external worker 扮演 reviewer，否则不要把本文件嵌入 worker prompt。

---

## EXTERNAL_WRITER_MERGE_RULE / REVIEW_MODULE

当一个 canonical artifact 使用多个 external writer draft 时，外部输出只能作为 advisory input，不能作为 canonical evidence。

硬规则：

1. Primary evidence 仍然只有原始 source surface
- 对 message / research source，是 embedded `read_content.md` 或明确嵌入的 source packet。
- 对 raw JSON / transcript source，是 embedded raw `text` / transcript。
- 对 deterministic packet，是 caller 明确嵌入的 packet body。
- 外部 writer draft、claims JSONL、metadata、run logs、reasoning logs 只能帮助 reviewer 找角度、错误、遗漏和 salience，不得作为事实来源。

2. Main agent 必须独立裁决
- 不能在多个 draft 中机械拼接句子。
- 必须回到 primary evidence 验证关键事实、数字、时间、hedge、因果链和不确定性。
- 多个 external writers 之间一致，不等于事实成立；只能说明这是值得复查的候选点。
- 外部 draft 与 primary evidence 冲突时，primary evidence 优先；不能为了保留 draft 文字添加兼容 shim。

3. Merge 输出必须是 reviewer-written baseline
- 最终稿应由 main agent 重写，不是“最佳外部稿 + 少量修补”。
- 可以吸收外部 draft 的好处：更好的 angle split、遗漏的 mechanism、保留细节、反例、salience 提醒。
- 必须删除外部 draft 的坏处：overclaiming、把 hedge 写成确定性、把机制写成官方意图、把背景材料抬成 primary、术语错误、未经 source 支撑的外部知识。

4. Salience 由 reviewer 负责
- 多个外部 draft 或多个候选角度不是等权切片。
- 外部 writer 可以建议 salience，但 canonical artifact 的 priority / salience / severity / gate status 必须由 main agent / human reviewer 最终决定。
- Primary 应给 source 的主信号和最可证伪的 synthesis input；secondary 给机制支撑和诊断；background 给结构背景、expression-only 或低置信候选。

5. Final judgment 必须显式记录
- 最终回复或 promotion note 需要说明采用了哪些外部 draft 的优点、拒绝了哪些点、剩余风险是什么。
- 如果只生成 draft，不 promote，也要明确说明不 promote 的原因。

---

## 使用边界

这个规则属于 caller / main-agent control plane。它可以用于 merge review、promotion note、handoff 和 audit log。

它不进入普通 external worker stable prefix。只有当 worker 的明确任务是“review external drafts and advise the caller”时，才可以把它作为 reviewer-specific `CUSTOMIZE_MODULE` 或 `DATA_DEPENDENT_MODULE` 的参考。

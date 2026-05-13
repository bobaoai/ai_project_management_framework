# Company Financial Report Preflight

> 在 writer 开始写报告之前跑一遍。三个问题全过，才允许进入写作；任何一个 fail，先补上游再回来。

---

## Gate 1: Package 有足够 benchmark

检查 `digestion_12` package 或 source card 里是否包含：

- [ ] 至少一组可比公司的 valuation multiple（带 unit-of-account：EV/revenue、P/E、preferred-round valuation/run-rate 等）
- [ ] 每个 benchmark 标注口径：public market price、preferred-round、secondary PPS、fund mark、issuer voluntary disclosure
- [ ] 如果目标是 private company：是否有 preferred-round vs common-share fair value boundary 的显式说明
- [ ] 如果涉及 secondary market：pricing surface 是否标注 firm/indicative、measurement date、retrieval date

**Fail 时怎么办：** 走 `digestion-independent-researcher` 补源 → source card → package 回灌，再回到本 gate。

---

## Gate 2: 所有数字 package-backed

对 writer 将要使用的每一个数字做 traceback：

- [ ] revenue / growth / margin / multiple / threshold / price → 能在 package field 或 source card 找到来源
- [ ] 没有 "calibration label" 式使用（例：把 Snowflake 12-15x 当 anchor 但 package 里没有 Snowflake source card）
- [ ] 如果 package 缺某个数字，且报告需要它 → 删除该数字，或先补源再写

**Fail 时怎么办：** 列出缺失数字清单 → 判断是否必要 → 必要则走补源流程；非必要则从 report grammar 中移除该段。

---

## Gate 3: Writer 只消费 deterministic narrative inputs + stable grammar

确认 writer prompt / package 没有混层：

- [ ] Package 里只有 facts：claim refs、source refs、数字、units、gaps、blocked uses、cannot-know fields
- [ ] Package 里没有 prose instruction、writer framing、report structure guidance
- [ ] Report grammar 由 `research_30_company_report_instruction.md` 负责（怎么让 PM 形成判断），不由 package 负责
- [ ] Cannot-Know section 是分析性的（"这个 gap 影响 PM 判断因为 X，证据 Y 能补齐"），不是免责模板

**Fail 时怎么办：** 把 prose instruction 从 package 移回 `research_30_company_report_instruction.md`；把 facts 从 writer prompt 移回 package。

---

## 适用范围

- `research-company-financial-analysis` 产出的所有 PM-facing report（public + private company）
- 同一 deliverable 的所有版本（Claude draft、DS draft、最终版）必须通过同一套 preflight

## 关联文件

| 文件 | 职责 |
|---|---|
| `designDoc/digestion_12_private_company_report_package_contract.md` | Package deterministic facts contract |
| `designDoc/research_31_private_company_report_instruction.md` | Report grammar（how PM forms judgment） |
| `.claude/skills/research-company-financial-analysis/SKILL.md` | Skill routing + result contract |
| `.claude/skills/digestion-independent-researcher/SKILL.md` | 补源流程 |

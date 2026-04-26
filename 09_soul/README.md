# 09_soul：Hoveath Portable Pluggable System

`09_soul/` 是 Hoveath 的 portable digital self，组织成一个可插拔系统：drop 整个 `09_soul/` 进任何 workspace，按 [`handoff/installation_guide.md`](handoff/installation_guide.md) 走一遍 bootstrap，就能让该 workspace 拥有：

- 跨项目稳定的判断方法（Philosophy）
- 跨项目稳定的角色 / 沟通风格 / 用户偏好（Identity）
- 跨项目稳定的执行 best-practice（Execution）
- 同步 source ↔ agent 投影的工具（Bridging）
- 项目 ↔ Hoveath upstream 的交接协议（Handoff）
- 真实项目的参考实现（Examples）

Hoveath 是被这一层承载的数字自我；09_soul 是承载的代码 / 文档容器。

## 这个仓库的定位（母仓库）

本仓库（`Hoveath/`）是 09_soul 的**母版本 / source-of-truth**。它不绑定某个具体 host workspace，承担三件事：

1. **维护 portable 层**：axioms / core / skills / bridging / handoff 的 canonical 版本在这里。
2. **接收反向蒸馏**：host 项目按 [`handoff/distillation_protocol.md`](handoff/distillation_protocol.md) 把稳定 lesson 回流到这里。
3. **作为 bootstrap 源**：新 workspace 直接从这里 clone / copy 09_soul/，按 installation_guide 走。

母仓库本身**不**搭运行时主投影（不放 `09_<agent>/` 与 `<entry-doc>`）。runtime 投影都在 host 项目里建立。examples/ 中保留真实项目的参考实现作为对照基线。

## Agent Runtime 立场

Hoveath 在 agent runtime 选择上保持 agnostic。当前已知投影范式：

- **Claude Code**：`<entry-doc>` = `CLAUDE.md`、投影目录 = `09_claude/` + `.claude/`
- **Cursor**：`<entry-doc>` = `AGENTS.md` / `.cursor/rules/`，仍可继承 09_soul，但已不是优先迭代方向
- **OpenCode / Codex / 其他**：handoff 协议预留扩展点，暂未沉淀模板

新 agent 投影按 `handoff/add_new_agent_projection.md`（待补）协议建立。

## 目录结构与层归属

```
09_soul/
├── README.md                 ← 本文件（bootstrap 入口）
│
├── core/                     ← Identity 层 source-of-truth
│   ├── SOUL.md               (character + 工作姿态)
│   ├── COMMUNICATION.md      (沟通风格 + Self-Review pointer + Retrospective trigger)
│   ├── USER.md               (跨项目 portable user profile)
│   ├── PROJECT_ADAPTER_TEMPLATE.md
│   ├── DEVELOPMENT_INTEGRATION.md
│   ├── LOCALIZATION_GUIDE.md
│   ├── PORTABILITY.md
│   ├── AGENTS_REFERENCE.md
│   └── WORKSPACE_REFERENCE.md
│
├── axioms/                   ← Philosophy 层（最高抽象）
│   ├── INDEX.md              (53 entries：FP + 20 A + 11 T + 10 M + 5 V + 6 X)
│   ├── FP_first_principles.md (最高优先级 axiom，先于所有其他)
│   └── A01..X06.md           (52 单点 axioms)
│
├── skills/                   ← Execution 层 best-practice 模板
│   ├── INDEX.md
│   ├── bestpractice_doc_self_review.md      (FP7 / R13 canonical 路径)
│   ├── bestpractice_retrospective_writing.md
│   ├── bestpractice_mirror_sync.md
│   ├── bestpractice_skill_writing.md
│   └── ...                   (parallel subagent / staged approach / debugging / 等)
│
├── bridging/                 ← bridging-management-layer
│   ├── README.md
│   ├── mirror_sync.py        (09_soul/core → 09_<agent>/core 物理 mirror 工具)
│   └── mirror_manifest.json  (外置 sync 状态，文档零 metadata；母仓库默认空)
│
├── handoff/                  ← 项目 ↔ Hoveath 交接协议
│   ├── README.md
│   ├── installation_guide.md     (Hoveath → 项目 bootstrap SOP，Phase 1-8)
│   ├── distillation_protocol.md  (项目 → Hoveath 反向蒸馏 SOP，S0-S8)
│   └── (待补) add_new_agent_projection.md
│
├── examples/                 ← 真实项目的参考实现
│   ├── README.md
│   └── trading_platform/
│       ├── claude_management_layer.md
│       └── PROJECT_ADAPTER_trading_platform.md
│
├── personas/                 ← 领域 persona pattern 范例
│   └── fed_watcher.md        (首个领域 persona pattern；可作为新 persona 模板)
│
├── tools/                    ← 业务工具（analytics / email / image gen 等，与 bridging 区分）
├── contexts/                 ← 历史上下文 scaffolding
├── docs/                     ← 历史 install / cron 参考
├── memory/                   ← 历史 observation 与 reflection
├── periodic_jobs/            ← 历史 cron 自动化骨架
└── reference/                ← 历史外部参考材料
```

## 四层语义边界

| 层 | 内容 | 跨项目 | 跨 agent | 修改入口 |
|---|---|---|---|---|
| Philosophy | axioms（含 FP） | ✅ | ✅ | `09_soul/axioms/` |
| Identity | SOUL / COMMUNICATION / USER profile | ✅ | ✅ | `09_soul/core/`（mirror 由 bridging/ 同步到各投影） |
| Working Environment | R-rules / task-scoped rules / routing | ❌ | ❌ | 各项目 `<entry-doc>` + `09_<agent>/rules/` + `09_<agent>/routing/` |
| Execution | skills + tools | best-practice ✅ / 业务 ❌ | best-practice ✅ / 业务 ❌ | `09_soul/skills/`（best-practice）/ `.<agent>/skills/`（业务） |

详细语义见 [`examples/trading_platform/claude_management_layer.md`](examples/trading_platform/claude_management_layer.md) §10。

## Bootstrap：把 09_soul drop 进新 workspace

按 [`handoff/installation_guide.md`](handoff/installation_guide.md) 的 Phase 1-8 SOP 走。简版步骤：

1. 复制 09_soul/ 到目标 repo
2. **Phase 1**：建 `09_<agent>/core/`，跑 `bridging/mirror_sync.py --register` 注册 SOUL/COMMUNICATION/USER mirror，写 `09_<agent>/core/PROJECT_ADAPTER.md`，写 `<entry-doc>`（CLAUDE.md / AGENTS.md / ...）含 Session Startup + First Principles + Core Rules
3. **Phase 2-5**：建 routing / rules / axioms / skills 各层（细节见 installation_guide）
4. **Phase 6**（仅老项目转 Hoveath）：旧 agent 投影降级
5. **Phase 7-8**：hooks 启用 + dogfood validation

参考 `examples/trading_platform/claude_management_layer.md` 看 Claude Code 投影的实际形态。

## Distill：把项目 lesson 回流母仓库

项目主投影 dogfood ≥1 周稳定后，按 [`handoff/distillation_protocol.md`](handoff/distillation_protocol.md) 的 S0-S8 步骤把项目内的 portable lesson 反向蒸馏回这个母仓库的 09_soul/ 与未来的 templates/。

蒸馏归属：母仓库（这个 repo），不在被蒸馏的项目内执行落盘。

## 维护协议

- **Identity 层 source-of-truth 在 09_soul/core/**：各 agent 投影里的 SOUL/COMMUNICATION/USER 是物理 mirror，由 [`bridging/mirror_sync.py`](bridging/mirror_sync.py) 维护一致性
- **Philosophy 层稳定**：axioms 跨项目跨 agent 通用；新 axiom 经过 ≥3 项目验证再加
- **编号守则**：axiom 编号一旦发布，先到先得，后到者重编号（参见 a20 frontmatter 的处理示例）
- **项目 lesson 反向回吐**：项目内积累的 portable 经验通过 `handoff/distillation_protocol.md` 蒸馏回母仓库，下一项目复用
- **Examples 是验证集，不是规范**：例项目展示「填完 templates 长什么样」，不能反向定义协议

## Quick Reference

| 想做的事 | 去哪 |
|---|---|
| 改判断方法 / philosophy | `axioms/`（先看 INDEX） |
| 改沟通风格 / 用户偏好 | `core/COMMUNICATION.md` / `core/USER.md`，host 项目内记得跑 `bridging/mirror_sync.py --apply` |
| 加跨项目 best-practice skill | `skills/`，更新 INDEX |
| 加项目特定 skill | `.<agent>/skills/`（在项目内，不在 09_soul/） |
| 同步 mirror（host 项目内） | `python 09_soul/bridging/mirror_sync.py --check` / `--apply` |
| 加新 agent 投影 | 看 `handoff/add_new_agent_projection.md`（待补），参考 `examples/trading_platform/` |
| 反向蒸馏 lesson | 看 `handoff/distillation_protocol.md` |
| 看「真实项目长啥样」 | `examples/<project>/` |
| 写新领域 persona | 参考 `personas/fed_watcher.md` 的 9-section 模板 |

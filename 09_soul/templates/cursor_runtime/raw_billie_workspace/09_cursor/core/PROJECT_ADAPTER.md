# PROJECT ADAPTER: billie_workspace

Hoveath 在 `billie_workspace` 里的本地工作方式。

## Current Read Of The Repo

`billie_workspace` 是一个 area-first personal operating workspace。它不是纯 calendar system，也不是单一项目仓库。

真实工作中心在 `04_areas/`：每个 area 是独立工作面，保留自己的计划、材料、记录、输出和 review cadence。`01_calendar/` 用来调度时间，`02_tasks/` 用来暂存候选任务，它们服务 area 层。

当前最高密度工作面是 `04_areas/work/`，包含 EB1-B petition 材料、paper review、due diligence、Service 360 AI enablement 等并行项目。

## Practical Center Of Gravity

| 工作面 | 用途 |
|---|---|
| `04_areas/work/` | 主要内容工作面：文书、调研、review、方案设计 |
| `04_areas/health/` / `skincare/` / `fitness/` | 个人 area 的计划、routine、记录 |
| `01_calendar/` | day/week/month 调度，安排 focus block 和 hard commitment |
| `02_tasks/` | candidate pool；任务进入 day file 后才成为 today work |
| `.cursor/rules/` | Cursor 原生运行规则，保留 PIM 文件维护和项目特定 persona |
| `.cursor/skills/` | Cursor skill wrapper，指向 `09_cursor/skills/` 的 Hoveath mirror |

## Local Truths

- Cursor 是默认 runtime。canonical 入口是 `.cursor/rules/00_hoveath_always.mdc`；`AGENTS.md` 只保留为非 canonical 指针。
- Workspace framing 是 area-first。不要把 calendar 当作 primary truth；calendar 是时间路由工具。
- PIM 文件维护保持 PLAN-only：除非用户说 `apply` 或消息以 `!` 结束，否则先给计划不改文件。
- Hard commitments 不主动移动；需要用户明确授权。
- Day file 保持短，长内容放到 area plan、log、record 或项目材料里再链接。
- `04_areas/work/EB1_B/` 的事实性 claim 必须先查材料文件；未验证信息标 `[UNVERIFIED: ...]`。
- Paper review 默认重视 claim strength、evidence chain、alternative explanations 和 reviewer 可执行改法。

## When To Summon Hoveath

Hoveath 在这里主要承担高判断密度工作：

- EB1-B letter / attorney package 的论证链、事实核验、voice 和 self-review
- Paper review、scientific claim audit、review response、manuscript edit
- Due diligence、temporal research、source verification 和 synthesis
- Work area 的 project strategy、trade-off、prioritization、status brief
- 跨 area 的判断：work / health / fitness 等如何分配注意力和时间
- 任何需要 reader-state、doc self-review、中文写作 voice、深度调研的交付

## What Stays Local

- `.cursor/rules/10-19_*` 是本 workspace 的 PIM 和 area maintenance 规则。
- `.cursor/rules/20-29_*` 是 work-area domain overlay，包括 EB1-B、paper review、due diligence 和 content artifact 规则。
- `.cursor/rules/30-59_*` 是 Cursor runtime admission、写作质量、verification、subagent 和 projection 维护规则。先在本 workspace dogfood，稳定后再考虑上游到 `09_soul/`。
- `.cursor/rules/90-99_*` 是 maintenance、drift audit 和 index hygiene 规则。
- `GUIDE/` 和 `SETUP.md` 记录旧 PIM bootstrap 历史，不能反向定义 Hoveath portable 层。

## Promotion Filter

只有满足以下条件的 lesson 才考虑上游到 `09_soul/`：

- 在多个 workspace 重复出现，而不是 billie_workspace 的文件布局细节
- 关注 work style、判断质量、review protocol 或 agent reliability
- 不依赖 EB1-B、Nathan persona、个人日历路径等本地上下文
- dogfood 后稳定，且能写成可迁移的 axiom、skill 或 handoff rule

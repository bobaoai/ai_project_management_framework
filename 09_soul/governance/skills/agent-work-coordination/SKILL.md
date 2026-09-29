---
name: agent-work-coordination
description: 通过 Orca CLI 管理持续运行、仅使用 Bash 的交互式 Claude Code 会话，交代代码或文档任务、追加要求、处理问题并按实际改动与验证结果验收。
metadata:
  skill_class: primary_agent_development
  primary_agent_entry_role: operator
  primary_agent_entry_subject: delegated_task
  first_authority_ref: designDoc/the_task_routing.md
---

# Claude Code 工作交接

## 1. Task

Primary Agent 使用 Orca 已有 CLI，把范围明确的代码或文档任务交给持续运行的 Claude Code，接收问题与交付，完成验收。Claude 只使用 Bash 读取和修改文件、运行 Git 与适用检查；任务结束后可以留在同一会话承接下一轮。

本 Skill 是 Portable 方法包中的可选操作能力，只有选用 Orca 时才检查该依赖，不要求所有项目安装或默认使用 Orca。本 Skill 负责交接与观察。项目的工程、写作和审核方法继续决定工作依据及质量要求，Orca 负责进程与消息接口。适用的正式独立审核仍通过本地 Agent Runtime 执行。

## 2. Reader Gain

管理者能交代一次工作，处理必要的决定，并用报告、准确改动和验证结果验收。执行者知道在哪里取得依据、怎样提出问题，以及完成后交出什么。正常工作无需从完整会话日志重建进展。

## 3. Entry and Exit

进入时，用户已授权当前代码或文档目标，并允许通过 Orca 委派。已有准确工作目录、允许修改范围、完成条件，以及本机可用的 Orca 与 Claude CLI。首次使用或版本变化时，核对实际 CLI 与本包 第 7 章的原生命令速查。同一会话沿用已确认的入口与引用，常用操作直接调用现成命令，不重新研究文档或新增包装层。

工具、登录或所需权限不可用时，保留具体错误并交对应环境负责人处理；其他不依赖该条件的工作可以继续。日常任务不自动安装厂商 Skills、修改全局 hooks 或权限策略。范围涉及生产数据、上线或其他应用操作时，取得该事项的具体授权与方法。

完成意味着产物满足要求、适用检查及独立审核有可核对结果、管理者接受交付，并为本次进程明确继续使用或清理。调用接受、回合停止或 worker 自述完成均不单独构成验收。

## 4. Execution Contract

### 4.1 Inputs and Authority

- 本次目标、工作目录、可修改范围、已有变更基线与完成条件；保留他人未提交的工作。
- 执行者需要读取的项目入口、设计与任务方法，以及可用检查命令。以准确路径提供材料，不预先复制整个仓库或历史聊天。
- 本机已确认的 Orca、Claude executable，任务指定的模型、effort 与权限模式。Auto 需要已有用户授权；不静默更换模型或启用 bypass。
- 已存在的 Orca workspace 和需要继续的 terminal、Run、Task、Dispatch 引用；仅使用产品真实返回值。
- 本次适用的本地 Agent Runtime 审核入口与执行配置，由项目负责人提供。

当前项目的 Task Routing 决定委派责任，所属设计决定任务含义。Portable 项目从 `designDoc/the_task_routing.md` 取得入口职责。本方法的执行分工是：Primary Agent 保留目标、沟通与验收责任，执行者在授权范围内完成任务，不再委派同一工作。项目路径由本次输入确定，不能假设安装本 Skill 的目录就是项目根目录。

### 4.2 Output and Completion

执行者提交实际文件和简短交接：完成什么；准确 commit 或文件差异；实际验证命令、结果及证据位置；失败、跳过和未完成项。复杂工作使用任务指定的报告文件；简单工作可直接用 Orca 消息承载。只提交本任务文件，不自动 push 或部署。

管理者核对消息属于当前 Task/Dispatch，再检查准确产物和关键 diff。代码负责取得 hash、文件范围、退出码和 Runtime 校验事实；管理者判断目标是否满足、意见是否成立及剩余风险。产物有新修改时，旧审核不得自动沿用。

## 5. Boundaries

| Boundary | Observable violation |
| --- | --- |
| 持续交互式 Claude | 每轮启动 print 调用或 resume，却声称一直是同一运行进程 |
| Bash-only 与实际权限分别处理 | 为消除错误启用其他工具、MCP、界面自动化、整套 Bash 免确认或 bypass |
| 原生产品承担通信 | 新建 controller、消息队列或同义任务 Registry；伪造 dispatch、capability 或 hook 事件 |
| 委派范围来自任务 | 修改全局配置、memory、安装库或业务数据，且没有相应授权 |
| 状态、交付与验收分别取证 | 将 hook 的 done、idle 或退出码直接当成代码正确和任务完成 |
| 日常观察保持有限 | 每轮重读完整日志，或将全部轨迹再次塞入下一轮 prompt |
| 正式独立审核由本地 Runtime 执行 | 用 worker 自审、Orca advisor 或直接 Provider 调用替代规定 Reviewer |

## 6. Method

### 6.1 交代结果和工作边界

写一段自包含的任务说明：目标、允许文件、先读哪些项目规则与依据、实际完成条件、检查方法和交付位置。代码任务提供复现方法；文档任务提供目标读者和必须保留的含义。提供完成任务需要的材料入口，让执行者自行用 Bash 检索。

明确执行者保持 Bash-only，不改变权限模式，不再派出执行者。通过本次 Orca 活跃 preamble 提供提问、心跳、消息与完成命令；准确 Task/Dispatch 及 capability 由产品注入，不能从历史报告复制。

### 6.2 启动并复用会话

按第 7 章，在准确 Orca workspace 内建立 shell，启动不带 `-p` 的 Claude，设置 `--tools Bash` 并使用本次授权的模型和权限。关闭不需要的 MCP、Chrome 与 IDE 自动接入。

普通项目运行保留已授权的原生 hooks 和项目入口规则；safe mode 只用于明确要求排除自定义配置的诊断或隔离试验。它会屏蔽 hooks、Skills 及自动项目指令，使用时须显式交代通过 Bash 读取哪些规则，并说明自动状态观测不成立。

确认 Claude 就绪后，用 `worker-start --terminal` 复用该进程派工。已有任务的追加发给当前 Dispatch；一轮已用 worker_done 结束后，下一轮使用同一 terminal 建立新 Task/Dispatch。保留必要的进程与 session 证据，不能用恢复历史代替持续进程。

### 6.3 处理问题、权限和状态

任务问题用 Orca ask/reply 往返；管理者使用 check 取得消息，处理后按产品规则 ack。超时后恢复原问题，不重复制造同一问题。消息入队不等于执行者已采纳，最终交付要说明追加要求如何落实。

hook 是原生状态观测。启用并被当前 Claude 加载时，权限请求可报告 waiting，活动报告 working，Stop 报告 done；普通 done 不承诺成功，也不代替 worker_done。启动前核对实际 hooks 状态，不能因 Orca 已安装就假定它们有效；没有 hook 证据时如实保留观测缺口。

工具权限使用宿主实际策略。Auto 会判断需要审查的动作，但不扩大本次授权。通过原始终端输出核对具体待决定动作；信息不完整或动作不明时报告缺口，不凭旧菜单猜测，不调整模式绕过拒绝。

正常只取新问题、短报告和 compact 状态。终端使用默认 `terminal read` 的 cursor/limit，不使用 `--screen`、桌面截图或 Computer Use。每五分钟的常规巡查只读取最新小段输出并记住已见位置；没有实质变化保持安静。具体失败、证据矛盾、审计或用户要求才扩大到相关时间窗口。hooks 上报到 Orca 不等于 Primary Agent 会自动获得一条消息，按实际公开接口消费状态。

### 6.4 验收和收尾

执行者运行适用检查，提交准确对象并通过活跃 preamble 的 worker_done 报告结果；发送后结束本次工作并等待。管理者阅读交接与关键 diff，再核对必要证据；新增失败或未解决风险才触发补测。

正式审核适用时调用项目已有方法：工程对象用 engineering-change-review，Skill 用 the-skill-authoring，均经本地 Agent Runtime。核对当前对象、执行事实、validator 与最终 verdict；调用完成不等于审核通过。

验收后决定立即复用、按用户要求保留，或使用产品 release。release 返回 retained/external_terminal 时，产品没有替管理者关闭进程；仅在确认归本任务所有、已空闲且不再需要后，关闭准确 terminal。响应丢失先查询原请求，不重复启动；缺少进程停止证据时不能宣称已停止或重新派一个并发修改者。保留当前产物与失败证据，向用户交付结果及真实未完成项。

## 7. 原生命令速查

### 7.1 入口与一次性准备

以下直接使用 `orca` 和 `claude` 命令名。宿主应使它们可在 PATH 中调用，或一次性提供准确 executable 替换命令名；同一会话沿用已确认的入口。Portable 包不保存本机绝对安装路径。

示例使用 POSIX shell；尖括号是需要填入的实际输入，不能原样执行。路径、任务文字和 JSON 使用正确 shell quoting，通过工具调用时优先传 argv 数组。正常操作无需新增包装程序。

```sh
command -v orca
command -v claude
orca status --json
orca agent hooks status --json
```

首次使用或版本发生变化时，使用安装版本的 `orca skills get orchestration`、`orca skills get orchestration --reference references/worker-contract.md` 和对应命令的 `--help` 核对接口。它们只读取说明，不安装 Skill。Orca 未启动时按授权用 `orca open`；宿主 sandbox 返回 EPERM 时，按宿主权限机制调用同一 CLI，不重装或改模式绕过。

选用已登记的准确 workspace，如 `path:/absolute/project`。可用 `orca repo list --json` 和 `orca worktree list --json` 查找。登记 Git 项目使用已授权的 `orca repo add --path <project> --json`；文件夹项目走当前产品已有的 project setup 入口，不擅自 git init。

### 7.2 启动一个交互式 Claude

已有可用协调者和 worker terminal 时直接复用；否则建立本次专用终端。命令使用宿主配置的 shell，不假设某台机器的绝对 shell 路径。

```sh
orca terminal create --worktree <workspace> --title work-coordinator --json
orca terminal create --worktree <workspace> --title work-claude --json
```

保存各自 `result.terminal.handle`。通过下面的原生入口，把完整 Claude 启动命令作为一个 text 参数交给 worker shell：

```sh
orca terminal send --terminal <worker> --text <完整且正确引用的启动命令> --enter --json
```

需要启动的命令是：

```sh
CLAUDE_CODE_AUTO_CONNECT_IDE=false CLAUDE_CODE_IDE_SKIP_AUTO_INSTALL=1 \
claude --model <model_id> --effort <effort> --tools Bash \
  --permission-mode auto --strict-mcp-config \
  --mcp-config '{"mcpServers":{}}' --no-chrome --disable-slash-commands
```

模型、effort 和 Auto 均以实际授权为准；没有 Auto 授权时使用本次指定的非 bypass 模式。不要增加 `--allowedTools Bash` 来预批准全部命令，也不加 print/resume 来代替持续进程。safe mode 只用于明确的隔离试验，它会关闭原生 hooks 及自动项目指令。

```sh
orca terminal wait --terminal <worker> --for tui-idle --timeout-ms 10000 --json
```

只有 `satisfied=true` 且进程仍运行，才继续派工。input_accepted 只表示输入已接受。原生确认的文字不完整时报告缺口，不根据旧输出或被截断的动作猜测；不使用 `--screen` 或桌面操作。

### 7.3 派工、追加和续一轮

```sh
orca orchestration run-create --objective <本次目标> --from <coordinator> --json
orca orchestration worker-start --run <run_id> --from <coordinator> --worktree <workspace> --terminal <worker> --task-title <短标题> --spec <完整任务说明> --timeout-ms 45000 --json
```

第一条返回 `result.run.id`。第二条保留 `result.taskId`、`dispatchId`、`state`、`stage` 和 `mutation.requestId`。复用 terminal 时，不再同时传 agent/model/effort；它们在进程启动时确定。原始含 capability 的回执留在私有证据位置，只向正常交接输出必要字段。

任务说明包含实际目标、允许文件、先读的规则与设计、检查命令、交付位置，以及保持 Bash-only、权限模式、不再委派、不修改全局配置的约束。示例：“修正指定模块的问题，先读所列项目规则与设计，仅改允许文件，按给定环境检查，交回准确 commit 或差异、结果及未完成项，不 push；业务问题和完成使用本次 Orca preamble 的命令，完成后留在此进程等待下一项任务。”这些描述仍须补入实际路径与验收要求。

任务未结束时追加指导：

```sh
orca orchestration send --to dispatch:<dispatch_id> --from <coordinator> --subject <追加要求摘要> --body <具体要求> --json
```

发送只保证入队，worker 在自然检查点读取。已发 worker_done 的一轮不能复用旧生命周期身份；下一轮在同一 worker terminal 再调用 worker-start，取得新 Task/Dispatch，不重启 Claude。

### 7.4 收件、回答和查看状态

```sh
orca orchestration check --terminal <coordinator> --wait --types question,worker_done,escalation --timeout-ms 45000 --json
orca orchestration reply --id <question_message_id> --from <coordinator> --body <回答> --json
orca orchestration check --terminal <coordinator> --ack <delivery_id> --json
orca orchestration worker-list --run <run_id> --json
orca terminal show --terminal <worker> --json
orca terminal read --terminal <worker> --cursor <nextCursor> --limit 30 --json
```

从 check 的 `result.deliveryId` 和 `messages` 处理整个返回批次后再 ack；未确认 delivery 重放时，不重复执行副作用。worker 的 ask 超时沿原 message ID 恢复。执行者提问、心跳、完成信号使用本次活跃 preamble 的准确命令和 capability；管理者不替它伪造报告。

worker-list 只取 attention、liveness、nextAction；terminal show 只取相关 agentWait 等字段。普通 read 使用 `result.terminal.nextCursor` 接续，无 cursor 时只取最新小段。三个连续空消息等待后按原生指南检查状态；缺少 hook 或 liveness=unverifiable 不代表进程已经停止。

hooks 的 waiting/working/done 更新 Orca 状态，不自动变成 check delivery。普通 Stop 的 done 可能没有成功结论，SessionStart 的 sessionBoundary 也不算任务完成。权限请求没有通用的 Claude approve/respond CLI，管理者不能仅凭 waiting 状态自动批准。

全局 hooks 变更由环境设置授权决定。已验证的 Orca 公开 CLI 只有 `agent hooks on/off/status`，没有单 Claude 开关；on 会按实际检测结果影响多种 Agent 配置。日常方法不自动开启，不调用私有 RPC 或自造 hook。不开 hooks 时继续显式 ask/worker_done，并如实保留主动状态观测缺口。

### 7.5 验收、复用与清理

读取准确报告和 diff，按第 6.4 节完成实际验收。需要立即继续时复用同一进程；用户要求留作调试时使用 `orca orchestration worker-retain --dispatch <dispatch_id> --json`。已结算且不再需要时：

```sh
orca orchestration worker-release --dispatch <dispatch_id> --json
```

`retained / external_terminal / processAction=none` 表示产品未关闭进程。确认该 terminal 是本任务创建、已空闲且不再使用后，才执行 `orca terminal close --terminal <handle> --json`；通过 `orca terminal list --worktree <workspace> --json` 核对，不批量关闭用户终端或删除工作区。

启动或发送结果不明时保留原 request ID、错误与回执，读取 failedStage、effects、residualResources 及原生恢复指示；必要时查 `orca skills get orchestration --reference references/recovery-and-cleanup.md`。只有确实适用时才用同一命令的 `--retry-request <原request_id>` 恢复，不能未知状态下重新创建并发执行者。

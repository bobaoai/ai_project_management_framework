---
name: agent-work-coordination
description: 通过 Orca CLI 在任务产出所属项目的 workspace 中管理持续运行、仅使用 Bash 的交互式 Claude Code 会话：交代代码或文档任务，处理问题、追加要求和目标变化，按实际改动、追加的处理回执与验证结果验收，并在工作结算或只待用户决定时结束监督等待。
metadata:
  skill_class: primary_agent_development
  primary_agent_entry_role: operator
  primary_agent_entry_subject: delegated_task
  first_authority_ref: designDoc/the_task_routing.md
---

# Claude Code 工作交接

## 1. Task

Primary Agent 使用 Orca 已有 CLI，把范围明确的代码或文档任务交给持续运行的 Claude Code：在任务产出所属项目的 workspace 中启动会话，由执行者从该项目入口找到工作方法，接收问题与交付，处理运行中的追加和目标变化，完成验收，并在没有可推进的工作时结束自己的等待。Claude 只使用 Bash 读取和修改文件、运行 Git 与适用检查；任务结束后可以留在同一会话，承接同一 workspace 的下一轮。

本 Skill 是 Portable 方法包中的可选操作能力，只有选用 Orca 时才检查该依赖，不要求所有项目安装或默认使用 Orca。本 Skill 负责交接与观察。项目的工程、写作和审核方法继续决定工作依据及质量要求，Orca 负责进程与消息接口。适用的正式独立审核仍通过本地 Agent Runtime 执行。

## 2. Reader Gain

管理者能为任务选对 workspace 和启动配置，交代一次工作，处理必要的决定，并用报告、准确改动和验证结果验收。管理者能用原生记录和回执分清一条追加只是入队、所在批次已被 ack、有执行者的明确处理回执，还是已经体现在交付中；目标、产物类别或所属 workspace 改变时，能判断应在原 Dispatch 内重新确定方法、另起 Task/Dispatch，还是换到所属 workspace。执行者知道从哪里取得依据和方法、怎样提出问题、完整处理收件批次并回报追加，以及完成后交出什么。正常工作无需从完整会话日志重建进展。管理者还能根据 Orca 返回的消息与结算状态判断是否继续等待，在没有可推进工作时停止等待和本任务的宿主唤醒。

## 3. Entry and Exit

进入时，用户已授权当前代码或文档目标，并允许通过 Orca 委派。管理者已按项目 Task Routing 确定所需结果、负责的 authority 和产出所属项目，能找到该项目在本机的准确 workspace，并已有允许修改范围、完成条件，以及本机可用的 Orca 与 Claude CLI。首次使用或版本变化时，核对实际 CLI 与本包第 7 章的原生命令速查。同一会话沿用已确认的入口与引用，常用操作直接调用现成命令，不重新研究文档或新增包装层。

所属项目或编写来源不能确定时，先向用户或该项目负责人问清，不按目录名、框架名或“母仓库”一类说法推定。例如同一方法或文档在多个项目各有安装副本，而用户尚未确认在哪一处编写和发布，就属于这种情况。

工具、登录或所需权限不可用时，保留具体错误并交对应环境负责人处理；其他不依赖该条件的工作可以继续。日常任务不自动安装厂商 Skills、修改全局 hooks 或权限策略。范围涉及生产数据、上线或其他应用操作时，取得该事项的具体授权与方法。

完成意味着产物满足最新目标，适用检查及独立审核有可核对结果，发给该 Dispatch 的每条追加都在交接中说明了处理结果并能在产物中核对，管理者接受交付，并为本次进程明确继续使用或清理。调用接受、消息入队、回合停止或 worker 自述完成均不单独构成验收。

监督等待在两种情况下结束：本任务的全部 Dispatch 已结算、其他已启动的独立执行（例如审核）已结束，且验收与问题已处理；或剩余事项只能由用户解除，也没有其他可独立推进的工作。此时停止当前等待，并停用本任务自建的宿主唤醒（第 6.6 节）。项目整体尚未完成不是继续等待的理由，暂停监督也不代表项目完成。

## 4. Execution Contract

### 4.1 Inputs and Authority

- 本次目标、所需产物类别、可修改范围、已有变更基线与完成条件；保留他人未提交的工作。
- 产出所属项目及其准确 workspace。它由项目 Task Routing 判断的负责方，以及用户确认的编写与发布来源共同决定。同一方法或文档在多个项目有安装副本时，只在已确认的编写来源修改，其他副本经既有安装或投影方法更新。
- 所属项目的入口文件（会话启动时自动读取的项目说明）及其指向的任务路由；执行者从这里找到工作方法。任务特有的设计、材料和可用检查命令以准确路径提供，不预先复制整个仓库或历史聊天。
- 本机已确认的 Orca、Claude executable，任务指定的模型、effort 与权限模式。Auto 需要已有用户授权；不静默更换模型或启用 bypass。
- 已存在的 Orca workspace 和需要继续的 terminal、Run、Task、Dispatch 引用，以及每个 Run 绑定的协调终端；仅使用产品真实返回值。
- 本次适用的本地 Agent Runtime 审核入口与执行配置，由项目负责人提供。它与日常会话的启动配置分开管理。
- 宿主为本次监督建立的定时唤醒或轮询（如有），以及当前宿主提供的暂停、停止和回读接口。它属于宿主；是否存在 Orca 消息触发宿主唤醒的绑定，须由当前宿主实际验证，不能仅凭消息已入队推定。

当前项目的 Task Routing 决定委派责任，所属设计决定任务含义。Portable 项目从 `designDoc/the_task_routing.md` 取得入口职责。本方法的执行分工是：Primary Agent 确定所需结果、负责的 authority 和所属 workspace，保留沟通与验收责任，目标改变时由它重新确定这些归属；执行者在这个既定范围内从项目入口找到并使用相应方法，开始前报告所选方法，缺件或冲突时回报，不自行改变业务归属，也不再委派同一工作。这是在执行端落实已经确定的入口，不是重做 Task Routing 第 6.4 节所指的顶层路由。项目路径由本次输入确定，不能假设安装本 Skill 的目录或协调者所在目录就是项目根目录。

### 4.2 Output and Completion

执行者提交实际文件和简短交接：开始实质工作前报告的方法选择；完成什么；准确 commit 或文件差异；实际验证命令、结果及证据位置；本 Dispatch 收到的每条追加的消息 ID 及处理结果；失败、跳过和未完成项。复杂工作使用任务指定的报告文件；简单工作可直接用 Orca 消息承载。只提交本任务文件，不自动 push 或部署。

管理者核对消息属于当前 Task/Dispatch 与预期 workspace，逐条核对该 Dispatch 收到的追加在交接中的处理，再检查准确产物和关键 diff 是否体现最新目标。代码负责取得 hash、文件范围、退出码、消息 ack 状态和 Runtime 校验事实；管理者判断目标是否满足、意见是否成立及剩余风险。产物有新修改时，旧审核不得自动沿用。

结束监督时向用户报告每个 Task 的结果与证据、仍保留的终端及原因、未解决的阻塞及需要谁决定，以及宿主唤醒停用的回读结果；停用失败时报告实际状态与具体阻碍。

## 5. Boundaries

| Boundary | Observable violation |
| --- | --- |
| 按产出所属选择 workspace | Claude 在协调者所在目录、与框架同名的目录或某个安装副本中启动，而产出属于另一项目或另一编写来源；目标转到另一项目后仍在原会话续写 |
| 日常会话保留项目入口与方法发现 | 日常启动带 `--disable-slash-commands`；用 `--safe-mode`、`--bare` 等关闭 CLAUDE.md 自动加载的模式却未另行交代入口；收窄设置来源或工具后没有核实项目入口与方法文件可达，就声称方法发现成立；把 Reviewer 的隔离配置套用到日常会话，或让日常会话代替 Reviewer |
| 方法由所属项目入口确定 | 管理者以在任务说明中点名 Skill 代替执行端的项目入口；执行者没有报告所选方法就开始实质产出 |
| 持续交互式 Claude | 每轮启动 print 调用或 resume，却声称一直是同一运行进程 |
| Bash-only 与实际权限分别处理 | 为消除错误启用其他工具、MCP、界面自动化、整套 Bash 免确认或 bypass |
| 原生产品承担通信 | 新建 controller、消息队列或同义任务 Registry；伪造 dispatch、capability、ack 或 hook 事件 |
| 委派范围来自任务 | 修改全局配置、memory、安装库或业务数据，且没有相应授权 |
| 入队、ack、采纳与落实分别取证 | 以 send 成功、wake、`read=1` 或 worker_done 宣称最新要求已落实；以 `read=0` 断定执行端从未取到；交接未说明某条追加或产物未体现它，却把交付接受为最新目标 |
| 收件批次完整处理 | 收件输出只保留数量或主题，丢掉 deliveryId、replayed、acknowledged 或消息正文；处理后不 ack；只看 ack 调用的 acknowledged 而丢掉它返回的下一批；对重放批次重复执行副作用 |
| 已结算 Dispatch 不再承接新要求 | 向已结算 Dispatch 追加或复用其 Task/Dispatch ID；为承接后续改写旧 Task 说明、旧交付或旧消息 |
| 状态、交付与验收分别取证 | 将 hook 的 done、idle 或退出码直接当成代码正确和任务完成 |
| 日常观察依靠原生消息 | 按固定间隔读取终端输出，每轮重读完整日志，或将全部轨迹再次塞入下一轮 prompt |
| 每个 Run 由其绑定的协调终端处理 | 以本终端 check 为空推断另一 Run 没有待处理消息；未经用户交接用 run-use 接管仍有协调者的 Run |
| 任务结算与进程保留分开 | 因 terminalState 为 retained、PTY 仍存活、liveness 为 unverifiable 或带有 attention 标记，把已结算的 Dispatch 当作执行中继续等待 |
| 监督等待有停止条件 | 全部结算并验收后，或只剩用户决定时，等待循环或本任务自建的宿主唤醒仍在运行；以项目整体未完为由续期 |
| 宿主唤醒与 Orca 分开 | 未经验证就声称 Orca 能暂停宿主 automation 或其消息会唤醒宿主；停用被拒绝后报告为已停，或改用其他接口、配置文件绕过 |
| 正式独立审核由本地 Runtime 执行 | 用 worker 自审、Orca advisor 或直接 Provider 调用替代规定 Reviewer |

## 6. Method

### 6.1 确定所属 workspace 并交代结果

先按当前项目的 Task Routing 判断所需结果、负责的 authority 和产出所属项目。workspace 跟随产出的编写来源：产出写入哪个项目、该项目的哪份源文件，Claude 就在那里启动。协调者自己所在的目录、框架名或目录名都不决定 workspace。同一方法或文档在多个项目各有副本时，以用户确认的编写与发布来源为准，下游副本经既有安装或投影更新；用户尚未确认时按第 3 章先问清。一项请求的各部分属于不同项目时，按所属拆成各自 workspace 中的 Task；执行者可以按准确路径读取其他项目的材料，写入只发生在本 Task 的所属 workspace。

写一段自包含的任务说明：目标结果和产物类别、所属项目与 authority、允许文件、实际完成条件、检查方法和交付位置，以及项目入口之外需要读取的任务材料。代码任务提供复现方法；文档任务提供目标读者和必须保留的含义。方法由执行者从所属项目入口找到：任务说明写清所需结果与所属，不以点名 Skill 代替项目入口。执行者报告的方法与路由依据不符时，管理者引用该路由位置纠正；执行者在正确 workspace 中仍找不到方法，说明入口、启动配置或路由本身有缺口，按第 6.2 节处理或交给相应负责人，不在每份任务里手写 Skill 名称来掩盖。

任务说明要求执行者：开始实质工作前，用本次 preamble 的 send 命令发送一条 `status`，说明所在 workspace、所选方法及其路由依据；在每个自然检查点及 worker_done 前收件，按第 6.3 节完整处理每个返回批次并 ack；收到管理者改变所需结果、产物类别或所属 workspace 的追加时，停在当前检查点，在新定范围内按第 6.4 节找到方法，并发送引用该消息 ID 的 `status`；自己发现工作可能属于其他项目或 authority 时用 escalation 回报，不自行改变归属；交接逐条列出收到的追加消息 ID 及处理结果。

明确执行者保持 Bash-only，不改变权限模式，不修改全局配置，不再派出执行者。通过本次 Orca 活跃 preamble 提供提问、心跳、消息与完成命令；准确 Task/Dispatch 及 capability 由产品注入，不能从历史报告复制。

### 6.2 启动并复用会话

按第 7 章，在所属 workspace 内建立 shell，启动不带 `-p` 的 Claude，设置 `--tools Bash` 并使用本次授权的模型和权限。关闭不需要的 MCP、Chrome 与 IDE 自动接入。

日常代码或文档会话要能读到所属项目的规则与方法。`--tools Bash` 会话不依赖原生 Skill 工具或 Skill 列表，已核实的此类会话中两者都不出现；执行者依靠启动目录自动加载的项目入口文件及其指向的路由找到方法，再用 Bash 读取对应的 `SKILL.md`。因此启动目录必须位于所属 workspace 内，并保留已授权的原生 hooks。方法是否可达，看项目入口和方法文件能否读到；本 Skill 不承诺去掉某个参数就会自动出现 Skill 列表。

日常启动不加 `--disable-slash-commands`，Claude CLI help 说明它关闭全部 Skills。按 help，`--safe-mode` 和 `--bare` 会关闭 CLAUDE.md 自动加载，只用于用户明确要求排除自定义配置的诊断或隔离试验；使用时在任务说明中交代改用 Bash 读取哪些规则，并说明哪些自动状态观测不成立。`--restricted`、`--setting-sources` 等参数改变加载的设置来源或可用工具，不能仅凭名称推断项目入口或方法文件不可达，也不能推断它们一定可达。确需按授权收窄配置时，以这次启动的实际核实为准：执行者的首个 `status` 指出已读到的项目入口和方法文件；无法证明时如实说明方法发现未经验证，不按已成立处理。

独立 Reviewer 需要与作者上下文隔离，这种隔离属于本地 Agent Runtime：所属审核入口按 Reviewer 的注册定义与执行参数调用它，不在 Orca worker 终端中运行，也不由本 Skill 指定参数。两类配置不互相套用。

确认 Claude 就绪后，用 `worker-start --terminal` 复用该进程派工，再用 worker-show 核对 Dispatch 所在 workspace 与预期一致。执行者的方法选择 `status` 到达后，对照所属项目路由核对；这一核对不需要执行者等待批准，发现不符时按第 6.4 节发出纠正。已有任务的追加发给当前 Dispatch；一轮已用 worker_done 结束后，同一 workspace 的下一轮使用同一 terminal 建立新 Task/Dispatch，其他 workspace 的工作在该 workspace 的终端进行。保留必要的进程与 session 证据，不能用恢复历史代替持续进程。

### 6.3 处理问题、权限和状态

任务问题用 Orca ask/reply 往返；管理者使用 check 取得消息，按下一段完整处理后 ack。超时后恢复原问题，不重复制造同一问题。

收件按批次处理，管理者与执行者相同。check 返回当前最早一个未 ack 的批次；这一批 ack 之前，每次 check 都以 `replayed=true` 重放同一批，之后入队的消息不会出现，因此漏 ack 会挡住后面的追加。每次收件保留 `result.deliveryId`、`replayed`、`acknowledged`，以及每条消息的 ID、类型、主题和正文；只输出数量或主题的压缩结果不算收件。逐条处理整批后，用该 deliveryId 执行 `check --ack`。ack 调用本身会接着取下一批，它返回的消息同样逐条处理并 ack，不能只看 `acknowledged` 而丢掉这一批，直到返回空批次。重放批次中已经处理过的消息不重复执行副作用，直接完成 ack。

hook 是原生状态观测。启用并被当前 Claude 加载时，权限请求可报告 waiting，活动报告 working，Stop 报告 done；普通 done 不承诺成功，也不代替 worker_done。启动前核对实际 hooks 状态，不能因 Orca 已安装就假定它们有效；没有 hook 证据时如实保留观测缺口。

工具权限使用宿主实际策略。Auto 会判断需要审查的动作，但不扩大本次授权。通过原始终端输出核对具体待决定动作；信息不完整或动作不明时报告缺口，不凭旧菜单猜测，不调整模式绕过拒绝。

正常交互走原生消息。执行者用 status 报告方法选择、用 ask 提问、用 escalation 报告阻塞、用 worker_done 交付，管理者用 `check --wait` 等这四类消息并处理整批交付。执行者的 heartbeat 按 preamble 的节奏发送，只证明它还活着，管理者不以它为唤醒条件，也不据此判断完成。宿主的定时唤醒（例如宿主 automation）是另一件事：它只在宿主不能长时间阻塞时把管理者带回同一个等待，不是巡查终端的理由。

只有出现具体问题、状态无法核实，或超过任务明确约定的时限，才按第 7.4 节读取相关的最小输出片段；单次 `check --wait` 为空或超时只是检查点，没有实质变化保持安静。证据矛盾、审计或用户要求时才扩大到相关时间窗口。hooks 上报到 Orca 不等于 Primary Agent 会自动获得一条消息，按实际公开接口消费状态。

一个协调终端在同一时间绑定一个 Run，consuming check 只返回该 Run 的消息。同时管理多个 Run 时，各 Run 的消息由其绑定的协调终端处理；task-list、worker-list 等查询用 `--run` 限定。管理者在本次已授权的 Run 内需要调整协调终端时，使用 run-use 并用 run-current 回读绑定；其他用户或任务的 Run 须先取得相应授权。

### 6.4 追加要求与目标变化

新输入先放回原任务判断。它只补充要求、不改变所需结果、产物类别和所属 workspace 时，作为追加发给当前 Dispatch；它改变其中任一项时，管理者先按 Task Routing 重新判断所需结果与所属，再决定执行端怎样承接。例如从现状调查方案改为编写通用 Design，读者、产物和负责的 authority 都变了，属于目标变化。

Orca 的原生记录能证明的事实有限，按下表分别取证：

| 要核对的事实 | 原生证据 | 不能证明什么 |
| --- | --- | --- |
| 追加已入队 | send 返回成功及 message ID | 执行端已经取到或已经阅读 |
| 所在批次已 ack | `inbox --terminal dispatch:<dispatch_id>` 中该消息 `read=1` | 执行端按正确顺序处理、理解、采纳或落实了要求。`read=0` 只表示尚未 ack，不能区分从未取到和取到后未 ack；`delivered_at` 不作为依据 |
| 执行端采纳 | 执行者引用该消息 ID 的明确处理回执，即 `status` 或交接中的说明 | 产物真的体现了要求，须对照产物核对 |
| 交付对应最新目标 | 管理者对照最新目标检查准确产物与 diff | worker_done 不关联任何追加；存在未 ack 的追加时，产品仍可接受 worker_done 并结算 |
| Dispatch 所在 workspace | worker-show 的 `startOptions.worktree` 与 `projection.workspace.id` | 执行者实际加载了哪些项目规则 |
| 执行端选用的方法 | 执行者开始实质工作前的 `status` | 方法执行质量 |

产品没有在存在未 ack 追加时阻止结算的门，也没有把交付与追加关联的字段。上表各项事实与对应关系由管理者在等待和验收时核对，不能写成已有代码硬拦。采纳以明确的处理回执为证，落实以产物和交接的核对为证；`read=1` 只是 ack 的事实。较早的追加仍为 `read=0` 时，若它所在批次已被返回过，之后入队的追加要等这一批 ack 后才会交给执行端；管理者从 inbox 无法区分它是否已被返回过，因此不能假定后发的目标变化已经送到。

**补充要求。** 用 `send --to dispatch:<dispatch_id>` 发送，向用户说明它已入队、待执行端处理并回执。之后每次被唤醒时查看该 Dispatch 追加的 ack 状态和处理回执；验收时按第 6.5 节逐条核对。

**目标或产物类别改变，所属 workspace 不变，Dispatch 仍在执行。** 追加中写明被替换的要求、新的所需结果和完成条件，并要求执行者在管理者新定的范围内从项目入口找到对应方法，在继续之前发送引用该消息 ID 的 `status`。这条 `status` 到达之前，即使 `read=1` 已经出现，也按执行端仍在做原目标处理，并如实告诉用户。等待回执时按第 6.6 节核对执行活动；执行者仍在运行时继续等待，不能因两次没有新消息而停止。全部执行已停止活动且剩余事项只能由用户解除时，说明尚缺的处理回执后结束等待。若 worker_done 先到，或交接没有体现该追加，这份交付只按它对原目标的实际完成情况验收；新目标在同一 terminal 用新 Task/Dispatch 承接。worker-start 把完整任务说明作为新的一轮输入交给执行端，这是让新要求确实进入执行端的原生途径。需要提前中断仍在执行的旧目标时，先核对已有授权和未完成的写入；用户已授权停止、改派或由管理者处理本任务进程时，可以使用 worker-stop，并收回实际停止结果。该命令会关闭 Claude 进程；超出已有授权或会影响共享任务时，再向用户取得决定。

**所属 workspace 改变。** 运行中的会话按启动目录加载项目入口，追加无法把它移到另一个项目。向当前 Dispatch 追加，要求执行者停止写入，并以 worker_done 和 `--outcome failed` 报告已完成部分与未继续的原因；然后在所属 workspace 按第 7.2 节启动或复用 Claude，用新 Task/Dispatch 承接。旧 Dispatch 没有回执或尚未结算时，新的执行者不修改与它允许范围重叠的文件；文件范围不重叠的工作可以先开始。

**已结算的 Dispatch。** 产品拒绝向已结算 Dispatch 追加，这一拒绝是最终结果，不改走其他通道送达。后续工作建立新 Task/Dispatch：任务说明自包含，以准确路径引用旧 Task/Dispatch ID 和旧产物作为材料，指定新的交付位置。旧任务说明、消息和交付保持原样，作为证据保留。

### 6.5 验收和收尾

执行者运行适用检查，提交准确对象并通过活跃 preamble 的 worker_done 报告结果；发送后结束本次工作并等待。管理者阅读交接与关键 diff，再核对必要证据；新增失败或未解决风险才触发补测。

接受交付前，以管理者本轮实际向该 Dispatch 发出的追加 message ID 为准（取自各次 send 回执），逐条在 `inbox --terminal dispatch:<dispatch_id>` 的结果中核对 `read`，并逐条对照交接与产物。inbox 结果按 `--limit` 截断，缺少某条已发出的消息或状态未知时，不宣称全部追加已 ack 或已处理；在本 Dispatch 范围内放宽 limit 重查后仍无法覆盖，就如实报告。交接没有说明某条追加，或产物没有体现它，这份交付就不能作为最新目标的完成：按其实际内容记录，未落实的要求按第 6.4 节用新 Task/Dispatch 承接，并向用户如实说明。`read=0` 不证明执行端从未取到，`read=1` 也不证明已经落实；某条追加在交接与产物中都已体现而仍为 `read=0` 时，记录缺少 ack 这一过程缺口，不单凭 `read=0` 否定交付。

正式审核适用时调用项目已有方法：工程对象用 engineering-change-review，Skill 用 the-skill-authoring，均经本地 Agent Runtime。核对当前对象、执行事实、validator 与最终 verdict；调用完成不等于审核通过。

验收后决定立即复用、按用户要求保留，或使用产品 release。release 返回 retained/external_terminal 时，产品没有替管理者关闭进程；仅在确认归本任务所有、已空闲且不再需要后，关闭准确 terminal。响应丢失先查询原请求，不重复启动；缺少进程停止证据时不能宣称已停止或重新派一个并发修改者。保留当前产物与失败证据，向用户交付结果及真实未完成项。

### 6.6 继续等待还是结束监督

本节先判断还有没有执行活动，再判断是否需要结束空巡查。监督范围包括本任务的子会话、worker、命令和独立 Reviewer 调用；只要其中任何一项仍在执行，就沿原任务或调用句柄继续有界等待、处理新事件并收回结果。暂时没有 stdout、两次收件为空或状态文字相同，都不能证明执行已经停止。已有截止的调用达到期限时处理准确失败，不重复发起调用。

**已确认所有子会话与独立执行都停止活动，且连续两次观察完全没有实质变化时，强制停止本次自动巡查。** 停止活动指本次执行已结束，或已明确停在只能由用户解除的等待点；不要求销毁留待复用的终端。先处理新问题、交付、追加回执和必要验收，有已授权且可推进的后续工作就继续推进，不能把待处理事项当成空巡查。随后比较同一监督范围的原生结果：Task/Dispatch 状态、问题、交付、追加的 ack 与处理回执、错误和结果。请求 ID、查询时间、等待耗时、分页或读取游标本身、相同消息的重复投递不算变化；heartbeat 只证明存活，不代表实质进展，也不能单凭它判断工作已经停止；实际执行活动仍按本节核对。只有全部停止活动且无待处理事项的前提已证实，比较结果又相同，才结束等待，用宿主接口暂停本任务的定时唤醒并回读确认。不再等第三轮，也不通过重置计数或换一种查询维持空转。只停止监督等待与唤醒，不取消任务或丢弃结果。

每次被消息或宿主唤醒带回时，先处理本任务尚未处理的原生交付：`check` 返回的整批消息逐条处理，核对方法选择、回答问题、核对 worker_done、完成验收和终端去向，然后 ack，并按第 6.3 节处理 ack 调用返回的下一批。之后核对本任务尚未结算的工作、未 ack 或没有处理回执的追加，以及已启动的其他独立执行；Orca 队列没有新消息不代表独立审核也已结束。worker-list 有后续页时按原生 page.nextCursor 取得本次范围内的完整结果，不能用第一页宣称没有剩余工作。Task 状态为 pending、ready、dispatched 或 blocked 时，工作仍未结算；completed 或 failed 表示已结算。

已结算的行即使 terminalState 为 retained、PTY 仍存活、liveness 为 unverifiable，或带有 requiresAction 而 nextAction 为 none 的 attention 标记，也不推翻已结算事实。处理能识别的未读交付或资源事项，按第 6.5 节决定去向；不把未说明的 attention 标签解释成任务又在执行。Orca 指南中“nextAction 为 none 时读取 liveness.reason 并继续 `check --wait`”适用于尚未结算的 Dispatch。`nextAction=none`、缺少 hook 或 `liveness=unverifiable` 均不证明子会话已经停止活动；状态未知时先按下表有界查明，不能套用全部停止活动后的空巡查规则。

| 情境 | 判断依据 | 动作 |
| --- | --- | --- |
| 完成待验收 | 收到当前 Dispatch 的 worker_done | 核对属于当前 Task/Dispatch 与预期 workspace，逐条核对追加的处理，按第 6.5 节验收并决定终端去向，再 ack；之后重新判断剩余工作 |
| 目标变化待回执 | 改变目标的追加尚无引用它的 `status` | 按第 6.4 节处理；向用户说明执行端仍在原目标上，不把入队或 `read=1` 说成已落实 |
| 全部停止活动，连续两次无变化 | 已确认所有子会话、worker、命令和独立审核均已结束或只待用户决定，无新交付或待处理事项，两次实质结果相同 | 强制结束空巡查，暂停本任务的宿主唤醒并回读；不停止或取消其他进程 |
| 仍有执行活动 | 任一子会话、worker、命令或独立审核仍在执行，包括暂时没有输出或两次原生状态相同 | 沿原任务或调用继续有界等待并处理新事件；不因消息暂时不变而结束等待，不例行读终端或重新派工 |
| 全部等用户 | 剩余事项只能由用户解除，没有其他可推进工作 | 向用户说明一次需要什么决定；停止等待，停用本任务自建的宿主唤醒并回读，然后等待用户消息 |
| 混合 | 部分事项等用户，另有 Dispatch 在执行 | 向用户说明待决事项；只为执行中的 Dispatch 保留等待，宿主唤醒只在这些等待需要时保留 |
| 未结算，状态不明 | Task 未结算，liveness 为 unverifiable 或结果未知 | 按 Orca recovery 指南有界查明：`worker-list --include-remote`、`worker-show`、有限的 `worker-read`。缺失证据不等于进程死亡，不凭沉默 stop、abandon 或重复派工。查明需要用户且没有其他活动工作时，报告并停用宿主空轮询 |
| 已结算，终端保留 | Task 为 completed 或 failed，terminalState 为 retained | 按已结算处理；需要时复用、按用户要求保留或 release。external_terminal 表示产品不会关闭该终端；不为它继续等待 |
| 全部结算并验收 | 没有未结算 Task 或其他运行中的独立执行，交付已处理并 ack，终端去向已决定 | 结束等待循环，用宿主接口停止或暂停本任务自建的唤醒并回读，向用户交付结果 |
| 停用失败 | 宿主拒绝，或回读显示唤醒仍在运行 | 向用户报告一次实际状态和具体阻碍；不说成已停，不换接口或改配置文件绕过，不重复同一调用；若之后仍被唤醒而阻碍和授权均未变化，直接结束，不再查询已知空队列、旧日志或反复写入相同等待记录。出现新证据或新授权时再处理 |

暂停监督只停止管理者自己的等待与唤醒，不代表项目完成，也不停止仍有实际工作的 worker。用户的新答复直接进入当前工作，不靠定时器发现。明确暂停过的监督不因时间到期自动恢复；只有新的具体委派或用户继续监督的授权才重新启用唤醒。宿主唤醒的建立、暂停和回读使用当前宿主的接口与权限，不假定 Orca 提供宿主 automation 控制或跨宿主自动唤醒；已有经验证的事件绑定时优先使用。

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

按第 6.1 节确定所属项目后，选用它已登记的准确 workspace，如 `path:/absolute/project`。可用 `orca repo list --json` 和 `orca worktree list --json` 查找。登记 Git 项目使用已授权的 `orca repo add --path <project> --json`；文件夹项目走当前产品已有的 project setup 入口，不擅自 git init。

### 7.2 启动一个交互式 Claude

所属 workspace 中已有可用的协调者和 worker terminal 时直接复用；否则在该 workspace 建立本次专用终端。命令使用宿主配置的 shell，不假设某台机器的绝对 shell 路径。

```sh
orca terminal create --worktree <owner_workspace> --title work-coordinator --json
orca terminal create --worktree <owner_workspace> --title work-claude --json
```

保存各自 `result.terminal.handle`。通过下面的原生入口，把完整 Claude 启动命令作为一个 text 参数交给 worker shell：

```sh
orca terminal send --terminal <worker> --text <完整且正确引用的启动命令> --enter --json
```

日常代码或文档会话的启动命令是：

```sh
CLAUDE_CODE_AUTO_CONNECT_IDE=false CLAUDE_CODE_IDE_SKIP_AUTO_INSTALL=1 \
claude --model <model_id> --effort <effort> --tools Bash \
  --permission-mode auto --strict-mcp-config \
  --mcp-config '{"mcpServers":{}}' --no-chrome
```

模型、effort 和 Auto 均以实际授权为准；没有 Auto 授权时使用本次指定的非 bypass 模式。不要增加 `--allowedTools Bash` 来预批准全部命令，也不加 print/resume 来代替持续进程。日常会话不加第 6.2 节列出的隔离参数；隔离试验需要用户明确要求，并按第 6.2 节交代缺失的能力。

```sh
orca terminal wait --terminal <worker> --for tui-idle --timeout-ms 10000 --json
```

只有 `satisfied=true` 且进程仍运行，才继续派工。input_accepted 只表示输入已接受。原生确认的文字不完整时报告缺口，不根据旧输出或被截断的动作猜测；不使用 `--screen` 或桌面操作。

### 7.3 派工、追加和续一轮

```sh
orca orchestration run-create --objective <本次目标> --from <coordinator> --json
orca orchestration worker-start --run <run_id> --from <coordinator> --worktree <owner_workspace> --terminal <worker> --task-title <短标题> --spec <完整任务说明> --timeout-ms 45000 --json
orca orchestration worker-show --dispatch <dispatch_id> --json
```

第一条返回 `result.run.id`，并把该 Run 绑定到 `<coordinator>`。第二条保留 `result.taskId`、`dispatchId`、`state`、`stage` 和 `mutation.requestId`；复用 terminal 时 `--worktree` 必须是该 terminal 所在的 workspace，不再同时传 agent/model/effort，它们在进程启动时确定。目标 terminal 仍有活跃 Dispatch 时，worker-start 会被拒绝，按第 6.4 节先处理原 Dispatch。第三条核对 `result.worker.startOptions.worktree` 与 `result.projection.workspace.id` 是否为所属 workspace。原始含 capability 的回执留在私有证据位置，只向正常交接输出必要字段。

任务说明包含第 6.1 节所列内容。示例：“在本项目内完成指定结果，产物属于所列 authority；先从项目入口找到对应方法，开始实质工作前用本次 preamble 的 send 命令发送 status，说明 workspace、所选方法和路由依据；仅改允许文件，按给定环境检查，交回准确 commit 或差异、结果、每条追加消息的处理及未完成项，不 push。每个自然检查点及 worker_done 前收件，保留 deliveryId、replayed、acknowledged 和每条消息的 ID 与正文，逐条处理整批后 ack，ack 返回的下一批同样处理；收到管理者改变所需结果、产物类别或所属 workspace 的追加时，停在当前检查点，在新定范围内找到方法并发送引用该消息 ID 的 status，所属 workspace 改变时停止写入并以 failed 报告；不自行改变业务归属。业务问题和完成使用本次 Orca preamble 的命令，完成后留在此进程等待下一项任务。”这些描述仍须补入实际路径与验收要求。

执行者处理完一个收件批次后的 ack 命令（handle 使用 preamble 中的准确值）：

```sh
orca orchestration check --terminal <worker> --ack <delivery_id> --json
```

它 ack 上一批后会接着取下一批；返回的 `messages` 非空时按第 6.3 节同样处理并 ack。

任务未结束时追加指导，并查看该 Dispatch 每条追加的 ack 状态：

```sh
orca orchestration send --to dispatch:<dispatch_id> --from <coordinator> --subject <追加要求摘要> --body <具体要求> --json
orca orchestration inbox --terminal dispatch:<dispatch_id> --limit 50 --json
```

send 成功只保证入队，worker 在自然检查点读取。inbox 只读，按 message ID 读取 `read`：`1` 只表示所在批次已 ack，`0` 表示尚未 ack；执行端只 check 不 ack 时，同一批次会重放且 `read` 保持 `0`。inbox 按 `--limit` 截断，核对覆盖以 send 回执中的 message ID 为准。是否采纳看执行者的明确处理回执，是否落实看产物。已发 worker_done 的一轮不能复用旧生命周期身份，产品会拒绝向它追加；同一 workspace 的下一轮在同一 worker terminal 再调用 worker-start，取得新 Task/Dispatch，不重启 Claude。

### 7.4 收件、回答和查看状态

```sh
orca orchestration check --terminal <coordinator> --wait --types question,worker_done,escalation,status --timeout-ms 45000 --json
orca orchestration reply --id <question_message_id> --from <coordinator> --body <回答> --json
orca orchestration check --terminal <coordinator> --ack <delivery_id> --json
orca orchestration task-list --run <run_id> --json
orca orchestration worker-list --run <run_id> --json
orca orchestration worker-show --dispatch <dispatch_id> --json
orca orchestration worker-read --dispatch <dispatch_id> --source terminal --limit 30 --json
orca orchestration run-current --from <coordinator> --json
orca orchestration run-show --id <run_id> --json
```

从 check 的 `result.deliveryId` 和 `messages` 处理整个返回批次后再 ack；未确认 delivery 会重放，重放时不重复执行副作用。ack 调用会接着返回下一批，带 `--wait` 时等待下一批，按第 6.3 节同样处理。worker 的 ask 超时沿原 message ID 恢复。执行者提问、心跳、状态和完成信号使用本次活跃 preamble 的准确命令和 capability；管理者不替它伪造报告或 ack。

task-list 的 status 区分未结算与已结算。worker-list 用 `--run` 限定本 Run，只取结算状态、terminalState、liveness、attention 与 nextAction；worker-show 只取 observation.agentWait 与 workspace 等相关字段。worker-read 只在第 6.3 节所列情况下读取有限片段，并用返回的 cursor 接续；不使用 `--screen`、桌面截图或 Computer Use。run-current 显示当前协调终端绑定的 Run，run-show 的 `coordinator_handle` 显示某个 Run 绑定的协调终端。出现具体状态疑问时按原生指南检查；只有确认全部子会话及独立执行都停止活动、没有待处理事项且连续两次实质结果相同，才按第 6.6 节停用空巡查。仍有执行活动时继续等待。缺少 hook 或 liveness=unverifiable 不代表进程已经停止，也不使已结算的工作重新成为执行中。

hooks 的 waiting/working/done 更新 Orca 状态，不自动变成 check delivery。普通 Stop 的 done 可能没有成功结论，SessionStart 的 sessionBoundary 也不算任务完成。权限请求没有通用的 Claude approve/respond CLI，管理者不能仅凭 waiting 状态自动批准。

全局 hooks 变更由环境设置授权决定。已验证的 Orca 公开 CLI 只有 `agent hooks on/off/status`，没有单 Claude 开关；on 会按实际检测结果影响多种 Agent 配置。日常方法不自动开启，不调用私有 RPC 或自造 hook。不开 hooks 时继续显式 status、ask 与 worker_done，并如实保留主动状态观测缺口。

### 7.5 验收、复用与清理

读取准确报告和 diff，按第 6.5 节完成实际验收。需要立即继续时复用同一进程；用户要求留作调试时使用 `orca orchestration worker-retain --dispatch <dispatch_id> --json`。已结算且不再需要时：

```sh
orca orchestration worker-release --dispatch <dispatch_id> --json
```

`retained / external_terminal / processAction=none` 表示产品未关闭进程。确认该 terminal 是本任务创建、已空闲且不再使用后，才执行 `orca terminal close --terminal <handle> --json`；通过 `orca terminal list --worktree <workspace> --json` 核对，不批量关闭用户终端或删除工作区。

```sh
orca orchestration worker-list --run <run_id> --terminal-state reclaimable --json
```

这个过滤结果只用于核对已结算终端的回收事项；为空不证明所有 Task 已结束。retained 表示进程被保留，不能据此推定任务仍在执行。结合完整任务状态、其他独立执行和已处理交付，按第 6.6 节决定是否结束等待与宿主唤醒。

启动或发送结果不明时保留原 request ID、错误与回执，读取 failedStage、effects、residualResources 及原生恢复指示；必要时用 `orca orchestration request-show --request <request_id> --json` 查询原请求是否已生效，或查 `orca skills get orchestration --reference references/recovery-and-cleanup.md`。只有确实适用时才用同一命令的 `--retry-request <原request_id>` 恢复，不能未知状态下重新创建并发执行者。

# 理论证据包 — 05 分层控制与慢快双速 (Phase 1)

> 本文件是「控制理论 ⊗ Agent 设计知识库」Phase 1 检索产物。权威性遵循契约区分级：理论/原理类 ≥2 独立权威源交叉验证。
>
> 检索日期：2026-09-07　检索方式：search-worker 多路并行（MIT OCW 6.231 Bertsekas + Sutton&Barto RL-book + ReAct ICLR paper + Sutton/Precup/Singh 1999 原始论文）

---

## KT-ctrl-041 分层控制结构（时间尺度分层）

- **定义**：分层控制将系统控制分为多个时间尺度/抽象层：上层以较慢采样率做策略层决策，下层以较快速度执行高频动作层任务；决策层与执行层在时间尺度上解耦。
- **数学**：时间尺度分离模型含慢变量 x（上层）与快变量 z（下层），ẋ=f(x,z,u)，ε·ż=g(x,z,u)，ε 为小参数；上层用慢时间尺度 τ=εt 决策，下层在原时间尺度执行。
- **Agent 映射**：Agent 的慢/快双速控制器。高层 Planner（慢、低频、抽象，负责目标规划与策略选择）+ 低层 Executor（快、高频、具体，负责每步动作/工具调用）。与 Daily/Deep variant（快/慢思考）及 Planner-Executor 架构同构。

### 📚 证据来源
| SRC | 级别 | 信源 | URL | 置信度 |
|-----|------|------|-----|--------|
| SRC-041a | S1 | MIT OCW 6.231 Bertsekas Dynamic Programming | https://ocw.mit.edu/courses/6-231-dynamic-programming-and-stochastic-control-fall-2015/ | 高 |
| SRC-041b | S2 | Sutton & Barto《RL: An Introduction》Ch.17 | http://incompleteideas.net/book/RLbook2020.pdf | 高 |

---

## KT-ctrl-042 递阶/多层控制

- **定义**：多层控制按层级组织控制器，每层对下层施加约束/目标（上级约束下级），上层解决协调问题，下层保持自主性。Mesarović 提出「交互预判原理」，上层修正下层耦合变量达成全局最优。
- **数学**：上层协调变量 λ 优化全局 min_u J(u)=ΣJ_i(u_i)，s.t. g_i(u_i,λ)≤0；下层在给定 λ 下独立求子问题 min J_i(u_i)；上层更新 λ 逼近全局最优（Interaction Prediction Principle）。
- **Agent 映射**：多层 Agent 栈。策略规划层（定目标+约束）与各领域子 Agent 层（父层约束下独立执行）；上层通过 skills/上下文约束下层决策空间。父 Agent 委派子 Agent=上层施约束、下层自主解。

### 📚 证据来源
| SRC | 级别 | 信源 | URL | 置信度 |
|-----|------|------|-----|--------|
| SRC-HIER-01 | S1 | Mesarović, Macko & Takahara《Theory of Hierarchical, Multilevel Systems》(1970) | https://archive.org/details/theoryofhierarch0068unse | 高 |
| SRC-HIER-02 | S1 | Mesarović et al. "Two Coordination Principles..." Automatica 6(1970) 323-331 (Interaction Prediction Principle) | https://doi.org/10.1016/0005-1098(70)90097-x | 高 |
| SRC-HIER-03 | S1 | Mesarović "Multilevel Systems and Concepts in Process Control" Proc. IEEE 58(1) 1970 111-125 | https://ieeexplore.ieee.org/document/1449475/ | 高 |

> ✅ **已补强**：多层递阶控制经 Mesarović 原著（Internet Archive digitized，1970）+ 两篇 Mesarović 原始论文（Automatica / Proc. IEEE）三 S1 一手源交叉验证，覆盖交互预判原理/协调原则。置信度升为「高」。原 ScienceDirect 聚合弱源已移除。`[VERIFIED-S1]`

---

## KT-ctrl-043 时间尺度分离（慢决策/快动作）

- **定义**：系统可分解为时间尺度分离的快/慢两组动力学：慢子系统携带宏观决策状态，快子系统携带微观执行状态；通过奇摄动方法在 ε→0 极限下将快动态在慢流形上投影掉，简化设计。
- **数学**：奇摄动标准形 ẋ=f(x,z,u)（慢），εż=g(x,z,u)（快）；令 z=h(x,u) 为 g=0 的准稳态流形，降阶模型 ẋ=f(x,h(x,u),u)；ε>0 时边界层误差以 O(ε) 收敛。
- **Agent 映射**：慢变量=高成本/低频率/抽象的 Planner（主干任务规划）；快变量=低成本/高频率/具体的 Executor（单步工具调用）。ε 对应快/慢层调用成本或频率比。快控制器在慢控制器给定的准稳态流形上做最优动作。

### 📚 证据来源
| SRC | 级别 | 信源 | URL | 置信度 |
|-----|------|------|-----|--------|
| SRC-043a | S2 | Wikipedia Singular Perturbation | https://en.wikipedia.org/wiki/Singular_perturbation | 高 |
| SRC-043b | S2 | Sutton & Barto《RL: An Introduction》Ch.17.2 | http://incompleteideas.net/book/RLbook2020.pdf | 高 |

---

## KT-ctrl-044 MPC 与滚动时域优化（RHC）

- **定义**：MPC 每个采样时刻基于当前状态与预测模型，在有限预测时域 N 内求解开环最优控制问题，但只执行第一步结果；随后时域前移、状态更新，问题重新求解，又称「滚动时域控制」。
- **数学**：min Σ_{k=0}^{N-1}ℓ(x_k,u_k)+Φ(x_N)，s.t. x_{k+1}=f(x_k,u_k)，x_k∈X，u_k∈U；仅执行 u₀*，下一时刻以新状态重新求解（时域前移一格）。
- **Agent 映射**：与 ReAct/规划-反思循环极度同构。MPC 预测时域内求解→只执行一步→状态更新→重新规划 = ReAct 的 Thought→Action+Observation→更新上下文→重新规划。预测时域 N≈前瞻步数；代价函数 J≈推理目标/评分；模型≈LLM world-model。

### 📚 证据来源
| SRC | 级别 | 信源 | URL | 置信度 |
|-----|------|------|-----|--------|
| SRC-044a | S2 | Wikipedia Model Predictive Control | https://en.wikipedia.org/wiki/Model_predictive_control | 高 |
| SRC-044b | S2 | Camacho & Bordons《Model Predictive Control》 | https://link.springer.com/book/10.1007/978-0-85729-398-4 | 高 |
| SRC-044c | S1 | ReAct (Yao et al., ICLR 2023, arXiv:2210.03629) | https://arxiv.org/abs/2210.03629 | 高 |

---

## KT-ctrl-045 规划-执行解耦（Plan-and-Execute）

- **定义**：将任务求解拆成两个解耦阶段：上层规划器（Planner）在初始/当前状态生成高层步骤序列（plan），下层执行器（Executor）逐步骤执行并把实际结果/观察反馈回规划器，使规划器可修正或重规划。
- **数学**：规划器 π_plan(s,g)=(a₁,…,a_n)；执行器逐步 a_t=π_exe(a_t,o_t)，o_t 为执行后观察；两层通过契约接口（plan 级 vs 动作级）交换。
- **Agent 映射**：精确对应 Agent 的 Plan-and-Replan 方法论：高层 Planner（慢、任务级规划，生成 milestone/契约文件）+ 低层 Executor（快、单步执行/工具调用）；观察反馈回调 Planner 重规划=MPC 滚动修正落地。

### 📚 证据来源
| SRC | 级别 | 信源 | URL | 置信度 |
|-----|------|------|-----|--------|
| SRC-045a | S1 | ReAct (Yao et al., ICLR 2023, arXiv:2210.03629) | https://arxiv.org/abs/2210.03629 | 高 |
| SRC-045b | S2 | Sutton & Barto《RL: An Introduction》Ch.17.2 | http://incompleteideas.net/book/RLbook2020.pdf | 高 |

---

## KT-ctrl-046 分层强化学习 / options / SMDP

- **定义**：分层 RL 通过把 MDP 分层为子任务/选项（option）实现时序抽象。选项是 ⟨I,π,β⟩ 元组：I 是触发状态集，π 是闭环子策略，β 是终止条件函数。选项在 SMDP 上取多个时间步执行，低层动作是选项特例（β≡0）。
- **数学**：选项 ω=⟨I_ω,π_ω,β_ω⟩；分层 Bellman v(s)=Σ_{ω∈Ω(s)}π(ω|s)[r(s,ω)+Σ_s' p(s'|s,ω)v(s')]；选项转移 p(s'|s,ω)=Σ_{k=1}^∞γ^k·Pr{S_k=s',τ=k|S₀=s}，奖励 r(s,ω)=E[R₁+γR₂+…+γ^{τ−1}R_τ]。
- **Agent 映射**：直接对应 Agent 分层语义。高层策略从 options 集合（=skills/子 Agent 能力原语）里选一个子任务执行；子任务=一个 skill/工具调用序列（对应 option 内部策略 π），直到完成条件（对应 β）。时序抽象把多步细节折叠成高层动作。

### 📚 证据来源
| SRC | 级别 | 信源 | URL | 置信度 |
|-----|------|------|-----|--------|
| SRC-046a | S1 | Sutton & Barto《RL: An Introduction》Ch.17.2 | http://incompleteideas.net/book/RLbook2020.pdf | 高 |
| SRC-046b | S1 | Sutton, Precup & Singh 1999 AIJ 112(1-2) | https://jair.org/index.php/jair/article/view/10079 | 高 |

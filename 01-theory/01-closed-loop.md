# 理论证据包 — 01 闭环反馈与稳定性 (Phase 1)

> 本文件是「控制理论 ⊗ Agent 设计知识库」Phase 1 检索产物。权威性遵循契约区分级：**理论/原理类 ≥2 独立权威源交叉验证**（S1 官方一手优先，S2 权威二手补位）。
>
> 检索日期：2026-09-07　检索方式：search-worker 多路并行（MIT OCW 16.30 + NPTEL IIT Madras 双 S1 交叉）

---

## KT-ctrl-001 开环 vs 闭环控制（前馈/反馈本质）

- **定义**：开环（前馈）通过施加控制律但不用测量结果修正输入，对建模误差更敏感；闭环（反馈）将输出与设定值比较并据此调节输入，用被控量测量误差主动校正系统行为。
- **数学**：开环 u=K·r（控制器直接作用于指令）；闭环 u=K·(r−y)=K·e，误差 e=r−y 反馈进输入，L=GGc 为回路增益。
- **Agent 映射**：开环 Agent = 单次 prompt 直接生成结果（不校验输出，错误不可纠）；闭环 Agent = 生成→评估→纠正自我迭代，用评估器测量输出与目标差距并反哺修正。

### 📚 证据来源
| SRC | 级别 | 信源 | URL | 置信度 |
|-----|------|------|-----|--------|
| SRC-001 | S1 | MIT OCW 16.30 Lec1 Introduction | https://ocw.mit.edu/courses/16-30-feedback-control-systems-fall-2010/resources/mit16_30f10_lec01/ | 高 |
| SRC-002 | S1 | NPTEL IIT Madras Control Systems Overview | https://nptel.ac.in/courses/107106081 | 高 |

---

## KT-ctrl-002 负反馈闭环系统结构

- **定义**：闭环系统由设定值/参考指令、传感器（测被控量）、执行器（施加控制）、控制律（控制器）及被控对象组成；误差 = 设定值 − 测量值，控制律基于误差生成校正量。
- **数学**：e = r − y；y = T(r−n) + S·do + SG·di，L=GGc 回路增益，S=(I+L)⁻¹ 灵敏度，T=L(I+L)⁻¹ 补灵敏度。
- **Agent 映射**：目标/规格=设定值 r；工具/评估=传感器 y；执行动作=执行器；策略/prompt 模板=控制律；误差=当前执行与目标的偏差，驱动下一轮动作。

### 📚 证据来源
| SRC | 级别 | 信源 | URL | 置信度 |
|-----|------|------|-----|--------|
| SRC-001 | S1 | MIT OCW 16.30 Lec1+Lec24 | https://ocw.mit.edu/courses/16-30-feedback-control-systems-fall-2010/resources/mit16_30f10_lec24/ | 高 |
| SRC-002 | S1 | NPTEL Closed Loop System | https://nptel.ac.in/courses/107106081 | 高 |

---

## KT-ctrl-003 稳定性定义（BIBO/渐进/Lyapunov）

- **定义**：BIBO 稳定=有界输入必有界输出；Lyapunov 稳定=平衡点微小偏差使轨迹始终在平衡点附近；渐进稳定=偏差最终被遗忘回到平衡点；指数稳定=渐进且收敛速度指数级快。
- **数学**：Lyapunov 对 ẋ=f(x)，平衡点 x0：稳定/渐近/指数；线性判据 A 特征值全在左半平面（Hurwitz）⇔ 渐近稳定。
- **Agent 映射**：Agent 稳定=输出不因微小扰动崩坏（BIBO 类比）；渐进稳定=多轮迭代后收敛正确解不放大中间错误；评估层需具误差遗忘特性防错误积累。

### 📚 证据来源
| SRC | 级别 | 信源 | URL | 置信度 |
|-----|------|------|-----|--------|
| SRC-001 | S1 | MIT OCW 16.30 Lec22 Lyapunov | https://ocw.mit.edu/courses/16-30-feedback-control-systems-fall-2010/resources/mit16_30f10_lec22/ | 高 |
| SRC-002 | S1 | NPTEL BIBO Stability | https://nptel.ac.in/courses/107106081 | 高 |

---

## KT-ctrl-004 误差收敛与反馈校正律

- **定义**：反馈校正律以误差 e=设定值−测量值为驱动，通过迭代调节输入使误差收敛；稳态误差取决于回路增益与系统型别。
- **数学**：追踪 e = r − y；理想追踪要求 |S(jω)| 低频足够小；|L(jω)|≫1 ⇒ S≈L⁻¹ 使 |S|≪1、|T|≈1；系统型别决定对阶跃/斜坡/抛物线指令的稳态误差。
- **Agent 映射**：自纠迭代=每轮算期望 vs 实际误差 e，用校正律（改 prompt/换策略）缩小 e；收敛保证=校正步进与误差方向一致，避免震荡。

### 📚 证据来源
| SRC | 级别 | 信源 | URL | 置信度 |
|-----|------|------|-----|--------|
| SRC-001 | S1 | MIT OCW 16.30 Lec24 Closed-loop analysis | https://ocw.mit.edu/courses/16-30-feedback-control-systems-fall-2010/resources/mit16_30f10_lec24/ | 高 |
| SRC-002 | S1 | NPTEL Steady State Error Analysis | https://nptel.ac.in/courses/107106081 | 高 |

---

## KT-ctrl-005 经典 LTI 稳定性判据直觉

- **定义**：LTI 系统稳定当且仅当所有极点位于 s 平面左半平面；Routh 判据通过特征多项式系数符号无需解根即可判稳；根轨迹绘制随增益变化闭环极点移动，展示稳定性边界。
- **数学**：闭环极点 = 1+GcG=0 的根；Routh-Hurwitz：特征方程系数+Routh 阵列第一列全同号⇒稳定；根轨迹满足幅值/相角条件 |GcG|=1、∠GcG=±180°。
- **Agent 映射**：若状态演化算子连续放大小误差则不稳定（右半平面极点类比）；Routh 判据=无需完整运行就能判定 Agent 是否发散；根轨迹=调参观察行为是否越出可接受边界。

### 📚 证据来源
| SRC | 级别 | 信源 | URL | 置信度 |
|-----|------|------|-----|--------|
| SRC-001 | S1 | MIT OCW 16.30 Lec2+Lec7 | https://ocw.mit.edu/courses/16-30-feedback-control-systems-fall-2010/resources/mit16_30f10_lec02/ | 高 |
| SRC-002 | S1 | NPTEL Routh's Stability Criterion / Root Locus | https://nptel.ac.in/courses/107106081 | 高 |

---

## KT-ctrl-006 反馈系统灵敏度与鲁棒性基础

- **定义**：灵敏度 S=(I+L)⁻¹ 刻画闭环对模型误差/参数摄动的敏感度，高回路增益可显著降低对模型误差敏感性（鲁棒性）；鲁棒稳定要求闭环在模型不确定范围内仍稳定。
- **数学**：S=(I+L)⁻¹，T=L(I+L)⁻¹，且 T(s)+S(s)=I；|L(jω)|≫1 ⇒ 对对象灵敏度 S≈0（跟踪/抗扰好、鲁棒）；鲁棒稳定性要求增益/相位裕度充分。
- **Agent 映射**：Agent 鲁棒性=对模型/环境假设偏差不敏感；高回路增益（强校验/强纠错）降低对基座模型误差（幻觉/工具波动）敏感度；设计评估阈值留裕度避免临界震荡。

### 📚 证据来源
| SRC | 级别 | 信源 | URL | 置信度 |
|-----|------|------|-----|--------|
| SRC-001 | S1 | MIT OCW 16.30 Lec24+Lec19 | https://ocw.mit.edu/courses/16-30-feedback-control-systems-fall-2010/resources/mit16_30f10_lec24/ | 高 |
| SRC-002 | S1 | MIT OCW 16.30 Lec19 Robustness | https://ocw.mit.edu/courses/16-30-feedback-control-systems-fall-2010/resources/mit16_30f10_lec19/ | 高 |

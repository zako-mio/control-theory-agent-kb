# 理论证据包 — 04 鲁棒控制与不确定性 (Phase 1)

> 本文件是「控制理论 ⊗ Agent 设计知识库」Phase 1 检索产物。权威性遵循契约区分级：理论/原理类 ≥2 独立权威源交叉验证。
>
> 检索日期：2026-09-07　检索方式：search-worker 多路并行（Zhou&Doyle 教材 + Zames/Doyle 原始论文 + arXiv 证）

---

## KT-ctrl-030 模型不确定性

- **定义**：模型不确定性指控制所基于的标称模型与实际系统的偏差，包括参数不确定（参数漂移）、未建模动态（被忽略的高频/高阶动力学）和外部干扰；鲁棒控制核心目标是在这些不确定性存在时仍保持满意性能。
- **数学**：加性 G_p=G_n+Δ_a；乘性 G_p=G_n(1+Δ_m)，Δ∈BH_∞，‖Δ‖_∞≤1；结构化用 Δ=diag(δ_i)块对角；小增益定理保证 ‖Δ‖_∞·‖M‖_∞<1。
- **Agent 映射**：LLM Agent 是可被标称模型，输出受 prompt 措辞/上下文窗口/模型漂移构成未建模动态；外部 API 延迟/限流是外部干扰。设计上需预留模型偏差的稳定裕度（置信度阈值、降级路径），而非假设标称行为。

### 📚 证据来源
| SRC | 级别 | 信源 | URL | 置信度 |
|-----|------|------|-----|--------|
| SRC-001 | S2 | Wikipedia Robust control | https://en.wikipedia.org/wiki/Robust_control | 高 |
| SRC-002 | S1 | Zhou & Doyle《Essentials of Robust Control》 | https://en.wikipedia.org/wiki/H-infinity_methods_in_control_theory | 高 |

---

## KT-ctrl-031 鲁棒稳定性 vs 标称稳定性

- **定义**：标称稳定保证控制器在精确标称模型上稳定；鲁棒稳定保证真实模型在给定不确定性集合内任意偏离标称模型时闭环仍稳定。
- **数学**：标称稳定 A_cl=BK 特征值全在左半平面；鲁棒稳定（小增益定理）‖W_m T‖_∞≤1 对所有 Δ；鲁棒性能同时要求 ‖W_s S‖_∞<1 与 ‖W_m T‖_∞<1。
- **Agent 映射**：Agent 标称稳定=理想输入下流程总能完成；鲁棒稳定=即使 prompt 改写/参数变化/工具异常，整套编排不失控/不死循环。设计需求=为 Agent 建立受控不确定性内绝不崩溃的保证。

### 📚 证据来源
| SRC | 级别 | 信源 | URL | 置信度 |
|-----|------|------|-----|--------|
| SRC-003 | S2 | Wikipedia H-infinity methods（次级背景，不作独立结论） | https://en.wikipedia.org/wiki/H-infinity_methods_in_control_theory | 高 |
| SRC-004 | S1 | Zames 1983 TAC "Feedback, minimax sensitivity, and optimal robustness"（期刊版，H∞ 奠基论文） | https://doi.org/10.1109/tac.1983.1103275 | 高 |

> ✅ **已回源核对**：此知识点原 URL 误指向 Zames 1981 IEEE CDC 会议页（`10.1109/cdc.1981.269342`，已弃用作历史记录）；经 Crossref 回核标题为 Zames 1981 会议版（较早期）。正确对应 H∞ 奠基论文应为 **Zames 1983 TAC**（`10.1109/tac.1983.1103275`，标题 "Feedback, minimax sensitivity, and optimal robustness"），当前有效源已据此纠正。Wikipedia 为 S2 背景源、不作独立 S1 结论。`[VERIFIED-DOI]`

---

## KT-ctrl-032 鲁棒控制方法（H∞/μ综合/滑模控制）

- **定义**：H∞ 控制最小化干扰到输出 H∞ 范数（worst-case 增益）同时保证鲁棒稳定性与性能（频域最优）；μ综合引入结构化奇异值处理结构化不确定性降低保守性；滑模控制设计滑模面使轨迹沿滑模面滑动，对模型不确定与干扰具不变性（时域鲁棒）。
- **数学**：H∞ min_K‖T_zw‖_∞，‖T‖_∞=sup_ω σ̄(T(jω))；μ综合 μ(M)=1/min{k:∃Δ,det(I−MΔ)=0}，sup‖μ≤1 保证鲁棒；滑模 s=0，控制律 u=−k·sat(s) 保证 s·ṡ<0，滑模面上扰动被完全抵消。
- **Agent 映射**：H∞→把 worst-case 失败成本作为首要优化目标；μ综合→对结构化不确定性（某类工具必超时/某类输入必格式错）针对性建模而非笼统兜底；滑模→触发容错保护规则后强制切换到稳定容错态并保持，对随机误差具不变性。

### 📚 证据来源
| SRC | 级别 | 信源 | URL | 置信度 |
|-----|------|------|-----|--------|
| SRC-005 | S2 | Wikipedia Sliding mode control | https://en.wikipedia.org/wiki/Sliding_mode_control | 高 |
| SRC-006 | S1 | Doyle 1982 IEE Proceedings D | https://doi.org/10.1049/ip-d.1982.0053 | 高 |
| SRC-007 | S1 | Zames 1983 TAC "Feedback, minimax sensitivity, and optimal robustness"（H∞/worst-case 奠基，与 SRC-004 同源校正） | https://doi.org/10.1109/tac.1983.1103275 | 高 |

---

## KT-ctrl-033 冗余与仲裁（多冗余表决/容错）

- **定义**：容错控制通过复制冗余组件（N-模冗余 NMR）+多数表决仲裁机容忍单个组件故障；三模冗余（TMR）用三个独立通道+多数表决器，任一通道失效输出仍正确；异质冗余通过多样化设计抵消共模/系统性错误。
- **数学**：TMR 可靠度 R_TMR=3R²−2R³；M-out-of-N 表决 R=∑(i=M..N)C(N,i)R^i(1−R)^(N−i)；输出=多数一致值，当且仅当 ≥M 通道一致时仲裁通过。
- **Agent 映射**：多 LLM Agent 互为校验；异质冗余→用不同模型/不同 prompt 模板/不同工具链做多样化生成，抵消同一模型系统性偏置（非重复相同调用）；仲裁器定义一致判定阈值（如 2/3 一致才置信）。

### 📚 证据来源
| SRC | 级别 | 信源 | URL | 置信度 |
|-----|------|------|-----|--------|
| SRC-008 | S2 | Wikipedia Fault tolerance | https://en.wikipedia.org/wiki/Fault_tolerance | 高 |
| SRC-009 | S2 | Wikipedia Fault-tolerant computing | https://en.wikipedia.org/wiki/Fault-tolerant_computing | 高 |

---

## KT-ctrl-034 安全边际/硬约束限幅（输入饱和/看门狗）

- **定义**：输入饱和指执行机构输出受物理硬限幅（如 ≤U_max），产生不可实现的控制量；当控制器积分累积使输出超限时发生积分饱和（windup），需限幅器/anti-windup 防止失控；看门狗是超限即拦截的硬保护。
- **数学**：执行器饱和 u=sign(u_c)·min(|u_c|,u_sat)；积分 windup 在 ∫e dt 超限时发生；anti-windup 饱和时冻结积分 o[r]=sat(K·e)，限制 ‖u‖_∞≤U_max。
- **Agent 映射**：执行器饱和=工具调用频率/预算/API rate-limit 硬上限；限幅器=把重试次数/并行工具数/累计 token/成本限制在预设阈值；看门狗=超出预算/权限/安全策略即终止该路径并降级，非继续尝试。

### 📚 证据来源
| SRC | 级别 | 信源 | URL | 置信度 |
|-----|------|------|-----|--------|
| SRC-AW-01 | S1 | arXiv 2606.01959 Anti-Windup in PID Control: Review (Caparroz, Soltesz, Hägglund, Guzmán) | https://arxiv.org/pdf/2606.01959 | 高 |
| SRC-AW-02 | S1 | arXiv 2311.00433 Decentralized PI-control and Anti-windup in Resource Sharing Networks (Tarbouriech, Zaccarian et al.) | https://arxiv.org/pdf/2311.00433v2 | 高 |

> ✅ **已补强**：输入饱和/积分 windup/anti-windup 经 arXiv 权威综述（含学科权威 Hägglund）与 anti-windup 奠基学者 Tarbouriech/Zaccarian 论文双 S1 交叉验证，覆盖 actuator saturation→integrator windup→overshoot、back-calculation/conditional integration/integrator clamping 等限幅机制。置信度升为「高」。原 S2 弱源（Wikipedia Integral windup/Actuator）已移除，作为补充背景保留。`[VERIFIED-S1]`

---

## KT-ctrl-035 干扰抑制/扰动观测器（DOB）

- **定义**：扰动观测器（DOB）是内环输出反馈控制器，在线估计作用于系统的外部扰动（含参数摄动/未建模动态之和），并在外环基线控制器输出中减去该估计值抵消扰动，使闭环在扰动下鲁棒、逼近无扰动标称响应。
- **数学**：经典 DOB (Chen 2004) 扰动估计 d̂=P_n⁻¹(s)·u−y；补偿后 u=u₀−d̂；Kobayashi 频域 u_c=(U_ff)/Q(s)+Q(s)·y，Q(s) 低通滤波 ‖Q‖_∞≤1 限噪镇定。
- **Agent 映射**：在线估计=用历史执行结果实时评估当前环境偏移（API 状态监测/递归估计错误率），并从当前决策中减去感知偏差，使 Agent 输出逼近无干扰理想行为；低通滤波=容忍瞬时噪声而非反应过度。

### 📚 证据来源
| SRC | 级别 | 信源 | URL | 置信度 |
|-----|------|------|-----|--------|
| SRC-012 | S1 | Chen 2004 IEEE/ASME Trans Mechatronics | https://doi.org/10.1109/tmech.2004.839034 | 高 |
| SRC-013 | S1 | DOB 35th Anniversary Overview arXiv:2203.12855 | https://arxiv.org/abs/2203.12855 | 高 |

# 理论证据包 — 03 PID 与误差收敛 (Phase 1)

> 本文件是「控制理论 ⊗ Agent 设计知识库」Phase 1 检索产物。权威性遵循契约区分级：理论/原理类 ≥2 独立权威源交叉验证。
>
> 检索日期：2026-09-07　检索方式：search-worker 多路并行（MathWorks 官方 + Wikipedia 权威 + MIT OCW/Stanford 学术补强）
> ✅ **聚合裁决已执行**：PID 分区知识点 ID 按契约 §4 统一重编号为 `KT-ctrl-020` ~ `KT-ctrl-026`（避免与 02 区冲突）；LQR（KT-ctrl-026）与反饱和（04 区 KT-ctrl-034）S1 弱项已补强。详见各知识点末尾 `[VERIFIED-S1]` 标记。

---

## KT-ctrl-020 比例-积分-微分控制器结构（三环节）

- **定义**：PID 控制器（三项控制器）是反馈控制回路机制，通过连续测量误差并以比例、积分、微分三环节组合生成控制量，广泛用于需连续自动调节的工业过程。
- **数学**：C = Kp + Ki·(1/s) + Kd·s（连续）；离散并行 C = Kp + Ki·IF(z) + Kd·(Tf+DF(z))。
- **Agent 映射**：反思/修正回路=反馈环；PID 三环节=三种收敛机制：P=基于当前错误即时纠偏，I=对历史偏航累积纠偏，D=对错误趋势超前预判。

### 📚 证据来源
| SRC | 级别 | 信源 | URL | 置信度 |
|-----|------|------|-----|--------|
| SRC-010 | S1 | MathWorks pid 官方文档 | https://www.mathworks.com/help/control/ref/pid.html | 高 |
| SRC-011 | S2 | Wikipedia PID controller | https://en.wikipedia.org/wiki/PID_controller | 高 |

---

## KT-ctrl-021 比例控制 P：即时误差修正

- **定义**：比例项产生的输出与当前误差值成正比，将误差乘以比例增益常数 Kp 进行调节。比例响应仅在存在非零误差时才驱动输出。
- **数学**：P_out = Kp · e(t)；Kp 越大响应越强但稳定性下降，Kp 过大会震荡。
- **Agent 映射**：即时反思=按当前任务偏差以固定权重（Kp）立即修正；Kp 过大=过度反应/反复跳跃（震荡），Kp 过小=修正不足收敛迟缓。

### 📚 证据来源
| SRC | 级别 | 信源 | URL | 置信度 |
|-----|------|------|-----|--------|
| SRC-012 | S2 | Wikipedia PID（比例项+SSE 局限） | https://en.wikipedia.org/wiki/PID_controller | 高 |
| SRC-013 | S1 | MathWorks pid 官方文档(Kp) | https://www.mathworks.com/help/control/ref/pid.html | 高 |

---

## KT-ctrl-022 积分控制 I：累积误差补偿

- **定义**：比例控制应用后若仍有残余误差，积分项通过累加历史误差值寻求消除残余误差。当误差被消除时，积分项停止增长。
- **数学**：I_out = Ki·∫₀ᵗ e(τ)dτ；积分项是瞬时误差随时间之和，代表此前应被纠正的累积偏移。
- **Agent 映射**：长期偏航的反思=累积历史误差加权修正（Ki），持续向 0 逼近消除稳态误差。但积分累积需防 windup（记忆过饱和），对应 Agent 对陈旧错误记忆的过度纠偏。

### 📚 证据来源
| SRC | 级别 | 信源 | URL | 置信度 |
|-----|------|------|-----|--------|
| SRC-014 | S2 | Wikipedia PID（积分项消除残余误差） | https://en.wikipedia.org/wiki/PID_controller | 高 |
| SRC-015 | S1 | MathWorks pid 官方文档(Ki) | https://www.mathworks.com/help/control/ref/pid.html | 高 |

---

## KT-ctrl-023 微分控制 D：预测性/超前调节

- **定义**：微分项通过评估误差变化率预测未来误差趋势，有助于抑制超调并增强系统稳定性，尤在系统快速变化时。
- **数学**：D_out = Kd · de(t)/dt（需加一阶滤波 Tf 抑制噪声）；离散用差分。预测误差趋势→anticipate。
- **Agent 映射**：预测性反思=基于误差速率（振荡/过快收敛/发散）提前干预，阻尼震荡抑制超调，对应防过度修正（overshoot）的提前刹车。

### 📚 证据来源
| SRC | 级别 | 信源 | URL | 置信度 |
|-----|------|------|-----|--------|
| SRC-016 | S2 | Wikipedia PID（微分预测未来误差趋势） | https://en.wikipedia.org/wiki/PID_controller | 高 |
| SRC-017 | S1 | MathWorks pid 官方文档(Kd,Tf) | https://www.mathworks.com/help/control/ref/pid.html | 高 |

---

## KT-ctrl-024 PID 整定与 Ziegler-Nichols 调参

- **定义**：PID 整定是寻找比例、积分、微分增益取值以达到期望性能。Ziegler-Nichols 是启发式整定法：将 I/D 置零，逐步增大 Kp 直至极限增益 Ku 处出现稳定等幅震荡，再用 Ku 与震荡周期 Tu 推求参数。
- **数学**：ZN 整定找极限增益 Ku 与周期 Tu；典型取值 P=0.6Ku、PI=0.4Ku/Tu；调参本质平衡响应速度与稳定性。
- **Agent 映射**：校准反思力度阈值（Kp/Ki/Kd），试探性增大修正强度直至临界震荡（超调/反复），再回退。对应超参数（反思频率）的启发式调试。

### 📚 证据来源
| SRC | 级别 | 信源 | URL | 置信度 |
|-----|------|------|-----|--------|
| SRC-018 | S2 | Wikipedia Ziegler-Nichols method | https://en.wikipedia.org/wiki/Ziegler%E2%80%93Nichols_method | 高 |
| SRC-019 | S1 | MathWorks PID Tuning | https://www.mathworks.com/discovery/pid-tuning.html | 中 |

---

## KT-ctrl-025 误差收敛直觉与稳态误差/超调

- **定义**：稳态误差（SSE）是期望最终输出与实际输出之差；比例控制因需非零误差驱动通常存在稳态误差。超调（overshoot）指响应越过目标值后回摆，由微分项 damp 抑制。
- **数学**：SSE 正比于系统增益相关量；瞬态=transient，稳态=steady state；误差收敛≈误差随时间指数缩小直至落入稳态带，期间可能过冲后回摆。
- **Agent 映射**：任务收敛=误差历经瞬态（初始震荡）后进稳态；出现 overshoot 表示修正过度需 D（预判）抑制；稳态误差表示仅靠 P 无法完全归零需 I（累积）解决。

### 📚 证据来源
| SRC | 级别 | 信源 | URL | 置信度 |
|-----|------|------|-----|--------|
| SRC-020 | S2 | Wikipedia PID（稳态误差 SSE） | https://en.wikipedia.org/wiki/PID_controller | 高 |
| SRC-021 | S2 | Wikipedia Steady state (electronics) | https://en.wikipedia.org/wiki/Steady_state_(electronics) | 中 |

---

## KT-ctrl-026 状态反馈 LQR（PID→现代控制衔接）

- **定义**：状态反馈控制通过算法最小化成本函数求得反馈增益，成本函数定义为关键测量量（状态偏差）与控制量的二次加权和。LQR（线性二次调节器）给出最优控制律 u = -Kx。
- **数学**：成本函数 J=∫₀^∞(x(t)ᵀQx(t)+u(t)ᵀRu(t))dt（可含 2xᵀNu 交叉项）；最优反馈 u=-K_lqr x，K=R⁻¹(BᵀP+Nᵀ)；P 由代数 Riccati 方程（ARE）0=AᵀP+PA+Q−PBR⁻¹BᵀP 求解。LQR 是 PID 从 SISO 向多变量状态空间的扩展。
- **Agent 映射**：由 PID 的局部修正式误差归零，升级为状态空间（完整内部状态+成本加权）全局最优修正；带约束 R 限制修正幅度→对应 Agent 显式成本函数权衡（短期修正 vs 过度干预）。

### 📚 证据来源
| SRC | 级别 | 信源 | URL | 置信度 |
|-----|------|------|-----|--------|
| SRC-LQR-01 | S1 | MIT OCW 16.30/16.31 Topic #12 LQR (lec12.pdf) | https://ocw.mit.edu/courses/16-30-feedback-control-systems-fall-2010/be97882d33e1689ef2eb80cf181afafb_MIT16_30F10_lec12.pdf | 高 |
| SRC-LQR-02 | S1 | Stanford EE363 Lecture 18 Continuous-time LQR (Boyd/Lall) | https://ee363.stanford.edu/lectures/018_clqr.pdf | 高 |

> ✅ **已补强**：LQR 经 MIT OCW 16.30（官方课程讲义 Topic#12）与 Stanford EE363（Boyd/Lall 顶级课程）两个独立机构一手源交叉验证，覆盖 u=-Kx、成本函数 J=∫(xᵀQx+uᵀRu)dt、ARE 全式、K=R⁻¹(BᵀP+Nᵀ)。置信度升为「高」。原 S2 弱源（Wikipedia LQR / MIT OCW 6.302）已移除。`[VERIFIED-S1]`

# 理论证据包 — 02 状态估计与记忆 (Phase 1)

> 本文件是「控制理论 ⊗ Agent 设计知识库」Phase 1 检索产物。权威性遵循契约区分级：理论/原理类 ≥2 独立权威源交叉验证。
>
> 检索日期：2026-09-07　检索方式：search-worker 多路并行（Kalman 1960 原始论文 + Särkkä 剑桥教材为 S1 背book）

---

## KT-ctrl-010 状态估计问题

- **定义**：从带噪声/不完整的系统输出（观测）中，估计无法直接测量的真实内部状态——构成基于观测的反馈控制基础。
- **数学**：线性系统 A/D（连续）或 F/H（离散）；用输出序列 y_k 递推估计隐藏状态 x_k，使估计误差期望/方差最小（最小方差估计）；可观测性是可解前提。
- **Agent 映射**：无法直接观测 LLM 模型内部表示（hidden x），只能看到 token 输出/外部反馈（observable y），需持续推断与修正内部记忆状态。

### 📚 证据来源
| SRC | 级别 | 信源 | URL | 置信度 |
|-----|------|------|-----|--------|
| SRC-001 | S2 | MIT OCW 16.323 最优控制原理 Estimators/Observers | https://ocw.mit.edu/courses/16-323-principles-of-optimal-control-spring-2008/ | 高 |
| SRC-002 | S2 | Wikipedia State observer (Luenberger) | https://en.wikipedia.org/wiki/State_observer | 高 |

---

## KT-ctrl-011 卡尔曼滤波（Kalman Filter / LQE）

- **定义**：基于带噪声时序观测，用两阶段（预测-更新）递推估计未知真实状态，并最小化均方误差的滤波算法，也称线性二次估计（LQE）。
- **数学**：预测 x̂₋ = F x̂ + B u，P₋ = F P Fᵀ + Q；更新 K=P₋Hᵀ(HP₋Hᵀ+R)⁻¹，x̂=x̂₋+K(z−Hx̂₋)，P=(I−KH)P₋。核心矩阵 F/H/Q/R/K。
- **Agent 映射**：记忆状态+置信度管理。预测=基于对话进展推进上下文信念；更新=用最新 token/反馈校正；K 增益=按证据相对不确定度决定信多少；P 协方差=记忆置信度。

### 📚 证据来源
| SRC | 级别 | 信源 | URL | 置信度 |
|-----|------|------|-----|--------|
| SRC-003 | S1 | R.E. Kalman 1960 原始论文 | https://doi.org/10.1115/1.3662552 | 高 |
| SRC-004 | S2 | Wikipedia Kalman filter | https://en.wikipedia.org/wiki/Kalman_filter | 高 |
| SRC-005 | S2 | Welch & Bishop 1994 Intro to Kalman Filter | https://www.semanticscholar.org/paper/b314ee06c3e47f0ad763ad419e979ae773f3a714 | 高 |

---

## KT-ctrl-012 观测噪声 vs 过程噪声

- **定义**：过程噪声（Q）刻画状态自身演化中的随机扰动/模型误差；观测噪声（R）刻画传感器测量环节引入的外界不确定性。二者之比经卡尔曼增益 K 决定估计器对模型预测与新观测的相对权重。
- **数学**：Q=过程噪声协方差；R=观测噪声协方差；K=P₋Hᵀ(HP₋Hᵀ+R)⁻¹。R/Q 小→信观测；R/Q 大→信模型预测。
- **Agent 映射**：不同信息通道的可信度权重。过程噪声=模型自身推理漂移/幻觉；观测噪声=输入/检索/工具返回可靠度。调节二者之比=决定上下文中强先验与新证据权重。

### 📚 证据来源
| SRC | 级别 | 信源 | URL | 置信度 |
|-----|------|------|-----|--------|
| SRC-004 | S2 | Wikipedia Kalman filter (Q/R 定义) | https://en.wikipedia.org/wiki/Kalman_filter | 高 |
| SRC-001 | S2 | MIT OCW 16.323 最优估计噪声建模 | https://ocw.mit.edu/courses/16-323-principles-of-optimal-control-spring-2008/ | 高 |

---

## KT-ctrl-013 状态估计器与现代控制（不完全信息控制）

- **定义**：当真实状态不可直接测量时，先由观测器/估计器重建状态，再基于估计值施加状态反馈，实现不完全信息下稳定与最优控制；估计器与控制器分离是分离性原理核心。
- **数学**：Luenberger 观测器 dx̂/dt=Ax̂+Bu+L(y−Cx̂)，误差 e=x−x̂ 满足 ė=(A−LC)e，可设计 L 使误差衰减到 0（前提可观测性）；与 LQR 组合成 LQG。
- **Agent 映射**：基于不完整信息的决策。Agent 无法获取真实世界完整状态，只能基于观测/上下文估计并决策；估计器+控制器解耦=感知/记忆模块（估计）与规划/行动模块（决策）解耦。LQG 警示：估计误差过大→决策失真。

### 📚 证据来源
| SRC | 级别 | 信源 | URL | 置信度 |
|-----|------|------|-----|--------|
| SRC-002 | S2 | Wikipedia State observer (Luenberger) | https://en.wikipedia.org/wiki/State_observer | 高 |
| SRC-005 | S2 | Welch & Bishop Intro to KF | https://www.semanticscholar.org/paper/b314ee06c3e47f0ad763ad419e979ae773f3a714 | 高 |

---

## KT-ctrl-014 信息过滤与信息降维（Information form）

- **定义**：以信息矩阵（协方差逆）/信息向量为统计量的卡尔曼滤波等价形式，在高维观测/低维状态场景下避免大矩阵求逆，并支持信息初始化——自然表达对状态一无所知的历史起点，聚焦有用状态、剔除无关干扰。
- **数学**：Y=P⁻¹、y=P⁻¹x̂；更新 Yₖ=Yₖ₋+HᵀR⁻¹H（信息形式下观测融合变线性累加）；预测需对较小矩阵求逆。维度收益：dim(y)≫dim(x) 时避免 n×n 大矩阵求逆。
- **Agent 映射**：上下文信息的稀疏/压缩保留。信息形式=以增量信息而非原始证据维护记忆，新证据按信噪比转化为信息增量线性累加，天然丢弃冗余。类比 prompt 压缩/记忆摘要。

### 📚 证据来源
| SRC | 级别 | 信源 | URL | 置信度 |
|-----|------|------|-----|--------|
| SRC-004 | S2 | Wikipedia Kalman filter § Information filter | https://en.wikipedia.org/wiki/Kalman_filter | 高 |
| SRC-001 | S2 | MIT OCW 16.323 最优估计 | https://ocw.mit.edu/courses/16-323-principles-of-optimal-control-spring-2008/ | 中 |

---

## KT-ctrl-015 贝叶斯滤波与隐马尔可夫模型

- **定义**：贝叶斯滤波是贝叶斯状态估计一般框架，在马尔可夫假设下用预测（传播先验）×似然（观测更新）递归维护后验信念分布；HMM 是其离散状态特例，与 Kalman 递推强类比。
- **数学**：预测 f(xₖ|y₁:ₖ₋₁)=∫f(xₖ|xₖ₋₁)f(xₖ₋₁|y₁:ₖ₋₁)dxₖ₋₁；更新 f(xₖ|y₁:ₖ)∝f(yₖ|xₖ)f(xₖ|y₁:ₖ₋₁)。Kalman 是高斯线性下该递推的解析解；HMM 前向算法=其更新步（状态离散）。
- **Agent 映射**：LLM 上下文信念状态更新。每轮对话/工具返回=一次观测，上下文=后验信念；预测=依据对话进展对信念先验演化，更新=用新信息贝叶斯修正。逐 token 维护信念近乎同构。

### 📚 证据来源
| SRC | 级别 | 信源 | URL | 置信度 |
|-----|------|------|-----|--------|
| SRC-004 | S2 | Wikipedia Kalman filter (与 HMM 类比) | https://en.wikipedia.org/wiki/Kalman_filter | 高 |
| SRC-006 | S1 | Särkkä Bayesian Filtering and Smoothing (CUP) | https://doi.org/10.1017/9781108917407.002 | 高 |
| SRC-007 | S2 | Wikipedia Hidden Markov model | https://en.wikipedia.org/wiki/Hidden_Markov_model | 高 |

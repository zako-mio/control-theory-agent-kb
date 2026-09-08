# 全产品标准实验组 — README

> 实验组遵循契约 §9 标准记录模板 + §7 最小必要破坏性操作范围（可逆+受控故障注入）。
> 实验日期：2026-09-07（6 框架版）　v1.1 说明：2026-09-08
>
> **实验范围说明（v1.1）**：本实验组仅覆盖原 6 个开源框架（可实机/源码注入）。v1.1 新增的 14 款精装房产品**不做标准实验组**——多数为闭源商用（无源码、无授权），改用「源码级（开源）/文档级（闭源）」实证审计，见 `07-checkpoint/premium-evidence.md`。

## 实验矩阵

| 产品 | 版本/源码 | 实机/源码 | 实验1 正常 | 实验2 故障注入 | 实验3 上下文污染 | 实验4 超长循环 | 状态 |
|------|----------|----------|:---:|:---:|:---:|:---:|:---:|
| **opencode** | v1.18.29 本地 + 1.18.16 Windows参照 | 实机 `opencode run` | ✅ | ✅ | ⏳ | ✅(看门狗) | 完成 |
| **deepseek-harness** | v0.1.1-rc.2 | 源码可逆注入点 | ✅ | ✅ | ✅ | ✅ | 完成 |
| **PRIME** | best-radar/bradar-prime-agent | 源码可逆注入点 | ✅ | ✅ | ✅ | ✅ | 完成 |
| **hermes** | NousResearch/hermes-agent | 源码可逆注入点 | ✅ | ✅ | ✅ | ✅ | 完成 |
| **claude-code** | anthropics/claude-code | 源码可逆注入点 | ✅ | ✅ | ✅ | ✅ | 完成 |
| **codex** | openai/codex | 源码可逆注入点 | ✅ | ✅ | ✅ | ✅ | 完成 |

## 核心横向洞察（6 框架对比，主 Agent 终裁）

### 洞察1：E 环（评估）从「一致最弱」分化为「两派」
样板三产品（opencode/dsh/PRIME）共同判定 **E 环最弱**（无独立 Critic）；但新增三产品打破了这个单一结论：
- **hermes**：**有独立 Critic 体系**（verification_evidence 证据台账 + verification_stop 门控 + hermes verify 强验证器 + review 评审器）——E 环反转为「有专属基础设施」
- **codex**：**Guardian + Review 双独立评审器**（带 confidence_score 结构化 JSON）——E 环强（但只管单步正确性）
- **claude-code**：E 环靠**外挂 hooks 插件**（security-guidance 三层验证 + code-review 置信度过滤）——贴片式，未内置仍偏弱

**结论**：**「E 环最弱」是早期（无独立 Critic）产品的共性，而非 Agent 普遍规律**。成熟产品已把「独立评审器」作为一等公民（hermes/codex）。

### 洞察2：T 环（执行器）是 6 框架共同的「最强环」——成立
- opencode：shell 超时看门狗 + 权限 ask/deny + 输出截断
- dsh：三瀑布 + timeout-policy + read-only fail-safe + spill 限幅
- PRIME：RLM depth 限幅 + bash kill 升级 + snapshot 恢复
- hermes：tool_executor 并发/顺序门控 + 心跳 + deadline + 迭代预算
- claude-code：hooks 仲裁 + 权限/沙箱 + 预算看门狗 + 超时
- codex：OS 级三层沙箱（Seatbelt/bwrap+Landlock/RestrictedToken）+ 审批管线 + 超时看门狗

**结论**：**执行器安全（看门狗/限幅/沙箱）是 Agent 工程最成熟的环节**，6 框架无一例外都做到了硬约束。

### 洞察3：各产品最弱环分化（不再单一）
| 产品 | 最弱环 | 说明 |
|------|:---:|------|
| opencode | E | 无独立 Critic |
| dsh | E | 无 validator 模块 |
| PRIME | E | gate 默认空 |
| hermes | P | 缺 MPC 滚动重规划 |
| claude-code | E | 外挂贴片式 |
| codex | P | MPC 玩具级 |

### 洞察4：M 环普遍缺置信度（P 协方差）——6 框架共性问题
- 三者/六者记忆都只记事实不记"我有多确定"（PRIME 相对最好，带作用域/版本；hermes 带离散置信标记）
- codex/claude-code 压缩按长度阈值而非信息增量/信噪比

## 契约红线遵守确认

- 所有实验仅在 `/tmp/opencode` 隔离区 + 源码只读分析，未修改任何记忆系统文件
- opencode 实机用 `--pure` 隔离装配层协议干扰
- 其余 5 产品为源码可逆注入点分析（未实机破坏）
- 未删除/改写任何非 `/tmp/opencode/` 路径文件

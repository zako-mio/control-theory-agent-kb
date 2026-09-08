# 浏览器标签页管理

## 核心原则

使用 browser-harness（browser-use）进行网页交互时，**必须**管理 Chrome 标签页生命周期：

### 规则 1：用完即关

每次 `new_tab()` 打开网页并完成数据提取后，应当关闭该标签页。使用 CDP 关闭：

```powershell
powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\.config\opencode\scripts\close-chrome-tabs.ps1" -KeepFirst
```

### 规则 2：批量关闭提示

当一项任务的**所有浏览器读取全部完成后**（如爬取多页数据、访问多个详情页），**必须**用 `question` 工具询问用户：

> 浏览器任务已完成，当前 Chrome 中可能留有 N 个标签页。是否关闭所有标签页（保留第一个）？

选项：
- 「关闭所有标签页」— 执行 `close-chrome-tabs.ps1 -KeepFirst`
- 「保持打开」

### 规则 3：不在中途干扰

- 批量爬取/读取过程中**不要**每页都关闭（会影响速度）
- 等**整个任务阶段**完成后统一询问关闭

## 脚本说明

`close-chrome-tabs.ps1` 参数：
- `-All` — 关闭所有标签页
- `-KeepFirst` — 保留第一个标签页，关闭其余
- `-KeepUrlPattern "regex"` — 保留匹配 URL 的标签页
- 无参数 — 列出当前标签页，不执行任何操作

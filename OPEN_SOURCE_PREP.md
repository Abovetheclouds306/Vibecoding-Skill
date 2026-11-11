# OPEN_SOURCE_PREP — 公开前审计清单

状态：Owner 已确认 **MIT / Copyright (c) 2026 YunAbove**，并授权两仓改为 GitHub **Public**（2026-11-11）。  
行号以处理时为准；vendor 不得就地改，须经 Standard 发版后整体替换。

| # | 领域 | 状态 | 说明 |
|---|---|---|---|
| L1 | Skill 许可证 | **CLOSED** | 正式 [`LICENSE`](LICENSE)（MIT，YunAbove 2026）；`LICENSE-DRAFT` 标为已废止；`SKILL.md` `license: MIT` |
| L2 | Standard 再分发 | **CLOSED** | Standard v1.2.9 已授予 MIT；vendor 含 `LICENSE`；允许随 Skill 再分发 |
| L3 | 版权声明 | **CLOSED** | 随正式 LICENSE |
| P1 | HANDOFF 私有评审痕迹 | 部分 | 仍含 R4–R12 过程；可后续精简或迁 `docs/internal/` |
| P2 | HANDOFF 本地绝对路径 | **已 scrub** | 改为 `<worktree>/...` 占位 |
| P3 | vendor 内 `F:\DOSS_...` | **已过时** | v1.2.8+ vendor 已去私有化 |
| P4 | 私有仓链接 | **本轮处理** | 两仓改 Public 后链接即公开地址 |
| P5 | 提交者邮箱 / “Chris” | 待 Owner | 改 noreply 需历史重写（另批）；Owner 称呼可保留 |
| D1/D2 | vendor 示例/环境措辞 | 低 | 随 Standard；现行已大幅中性化 |
| V1 | Skill 版本仍 0.1.0 POC | 中 | 公开发版后可另提交统一版本（影响 marker） |
| V2 | `standard_vendored_sha256` 语义 | 低 | 已是 ZIP 哈希；文档已说明 |
| V3 | “本机”措辞 | 部分 | `references/06`、`vibecoding/README` 改为作者环境观测 |
| I1 | 非 Windows 干净机 | 仍 NOT_RUN | 公开后补 |
| I2 / R9-g | 卸载说明 | **已有** | 根 README + `vibecoding/README` §七 |
| A1 | 自动激活过宽 | **已收窄** | `SKILL.md` description 改为显式/点名触发导向 |
| R9-a | 换行 / vendor 字节 | 保持 | CI 已加 `vb_trust` |
| R9-b | 根 README | **已有** | 安装/校验/卸载/许可入口 |
| R9-c | Actions | **已有** | `.github/workflows/ci.yml`：`vb_trust` + unittest |
| R9-d | 评审痕迹 | 同 P1 | |
| R9-e | 中断恢复 | 文档已有 | |
| R9-f | 再分发许可 | **CLOSED** | 同 L2 |
| R10-a/b | 安全模型 | **已有** | 见根 `SECURITY.md` |
| R11/R12 | 信任根文档等 | 已合 | |
| R12-a | 公开树 / vendor | **本轮** | vendor = Standard **v1.2.9**（`b1ece9f` / ZIP `ddaba678…`） |

## 本轮已做（OSS-1.2.9）

- Standard：MIT LICENSE + tag `v1.2.9` + Release ZIP
- Skill：整体替换 vendor；`vb_trust` / `vb_init` / `SKILL.md` / 文档钉扎 v1.2.9
- 正式 `LICENSE`；废止 `LICENSE-DRAFT`
- 两仓 `gh repo edit --visibility public`（本轮收尾）

## 仍可后续

- 提交历史邮箱重写
- Linux/macOS 干净机复测
- Skill 版本号自 0.1.0 POC 升版（另批）

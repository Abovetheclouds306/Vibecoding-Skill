# OPEN_SOURCE_PREP — 公开前审计清单

状态：仓库仍为 **PRIVATE**。阶段 D（2026-11-11）起开始处理；**L1/L2/R9-f 仍阻断公开**（待 Owner 确认许可与再分发）。  
行号以处理时为准；vendor 不得就地改，须经 Standard 发版后整体替换。

| # | 领域 | 状态 | 说明 |
|---|---|---|---|
| L1 | Skill 许可证 | **阻断** | `SKILL.md` 仍 `Proprietary`；仅有 `LICENSE-DRAFT`。待 Owner 选定许可证 + 版权人/年份 → 正式 `LICENSE` |
| L2 | Standard 再分发 | **阻断** | vendor 随 Skill 分发；Standard 仍 `LICENSE-DRAFT` / COPYRIGHT-CHECKLIST 未完成。待 Owner 书面确认可再分发并完成 Standard 侧 LICENSE |
| L3 | 版权声明 | 待 L1 | 随正式 LICENSE 补充 |
| P1 | HANDOFF 私有评审痕迹 | 部分 | 仍含 R4–R12 过程；公开前可再精简或迁 `docs/internal/` |
| P2 | HANDOFF 本地绝对路径 | **本轮已 scrub** | 改为 `<worktree>/...` 占位 |
| P3 | vendor 内 `F:\DOSS_...` | **已过时** | v1.2.8 正式 vendor 已去私有化；2026-11-11 复查无命中 |
| P4 | 私有仓链接 | 待公开策略 | 公开时改公开地址或注明私有来源 |
| P5 | 提交者邮箱 / “Chris” | 待 Owner | 改 noreply 需历史重写（另批）；Owner 称呼可保留 |
| D1/D2 | vendor 示例/环境措辞 | 低 | 随 Standard；现行 v1.2.8 已大幅中性化 |
| V1 | Skill 版本仍 0.1.0 POC | 中 | 公开发版时单独统一版本（影响 marker，另提交） |
| V2 | `standard_vendored_sha256` 语义 | 低 | 已是 ZIP 哈希；文档已说明 |
| V3 | “本机”措辞 | **本轮部分** | `references/06`、`vibecoding/README` 改为作者环境观测 |
| I1 | 非 Windows 干净机 | 仍 NOT_RUN | 公开前补 |
| I2 / R9-g | 卸载说明 | **已有** | 根 README + `vibecoding/README` §七 |
| A1 | 自动激活过宽 | **本轮收窄** | `SKILL.md` description 改为显式/点名触发导向 |
| R9-a | 换行 / vendor 字节 | 保持 | CI 已加 `vb_trust` |
| R9-b | 根 README | **已有** | 安装/校验/卸载/许可入口 |
| R9-c | Actions | **本轮加 CI** | `.github/workflows/ci.yml`：`vb_trust` + unittest |
| R9-d | 评审痕迹 | 同 P1 | |
| R9-e | 中断恢复 | 文档已有 | |
| R9-f | 再分发许可 | **阻断** | 同 L2 |
| R10-a/b | 安全模型 | **已有** | 见根 `SECURITY.md` |
| R11/R12 | 信任根文档等 | 已合 | |
| R12-a | 公开树 / vendor v1.2.8 | **私有正式已就绪** | 公开仍待 L1/L2 |

## 本轮已做（阶段 D 预热，未公开）

- `.github/workflows/ci.yml`
- HANDOFF 绝对路径 scrub；SKILL description 收窄；平台能力文档措辞
- 本清单状态表刷新（P3/R9-b/I2 等）

## 未做（需 Owner）

- 正式 `LICENSE`（Skill + Standard）
- 仓库改 Public / 对外宣布
- 提交历史邮箱重写
- Linux/macOS 干净机复测

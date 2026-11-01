# OPEN_SOURCE_PREP — 公开前审计清单（仅审计，未修复）

状态：本仓库为 **PRIVATE**。以下是公开前必须由 Owner 决定/处理的发现；本轮按授权**只记录不修改**（vendor 目录更是禁止修改）。行号以本文件所在提交为准。

| # | 领域 | 发现（file:line） | 严重度 | 建议 |
|---|---|---|---|---|
| L1 | 许可证 | `vibecoding/SKILL.md:4` `license: Proprietary`；仓库无 `LICENSE` 文件 | 阻断公开 | Owner 选定开源许可证，新增 LICENSE 并改 SKILL.md:4 |
| L2 | 许可证 | vendor 标准自身条款仅指向 `vendor/vibecoding-standard/README.md`；需确认 Standard 是否允许再分发 | 阻断公开 | 确认 Standard 许可；必要时 Standard 侧发版补许可 |
| L3 | 版权 | 全仓无版权声明（grep `Copyright\|版权` 0 命中） | 中 | 随 LICENSE 补充 |
| P1 | 私有历史 | `HANDOFF.md` 全文为私有评审过程（R4–R8 分支、提交号、`%TEMP%\vbdev_r7/r8` 等），例 `HANDOFF.md:5,49,60,73,88,92,103` | 高 | 公开前精简或移出 |
| P2 | 本地路径 | `HANDOFF.md:5` `F:\DOSS_Project\_worktrees\...` | 高 | 删除 |
| P3 | 本地路径（vendor，不可就地改） | `vibecoding/vendor/vibecoding-standard/README.md:83`、`docs/Agent接入指南.md:57,60-63,67,101`、`templates/CLAUDE.md.template:13` 含 `F:\DOSS_Project\...` | 高 | 只能在 Standard 侧发新版后整体替换 vendor |
| P4 | 私有仓库链接 | `vendor/.../docs/Agent接入指南.md:20,60` 指向私有 `Abovetheclouds306/Vibecoding-Standard`；`PROVENANCE.md:7` 同 | 中 | 公开时说明来源为私有或改为公开地址 |
| P5 | 身份 | 提交作者 `hankaizhou <791934306@qq.com>`（全部提交）；`TODO.md:42-43`、`HANDOFF.md:56` 提及 "Chris" | 中 | Owner 决定是否改用 noreply 邮箱（需重写历史，须另批） |
| D1 | DOSS/Nexus 示例 | vendor：`AI_PROJECT_STANDARD.md:105`、`CHANGELOG.md:60,138,163`、`docs/Agent接入指南.md:76`、`docs/候选优化报告-v1.2.7.md:19`、`完整任务示例.md:3`（已声明为教学示例） | 低-中 | 属 Standard 内容，随 Standard 处理 |
| D2 | 内部环境描述 | vendor `CHANGELOG.md:89,121`、`agents/Claude-Code.md:71,76` 提及"本机自建网关" | 低 | 同上 |
| V1 | 版本标识 | `SKILL.md:7,15`、`vibecoding/README.md:1`、`scripts/vb_init.py:46`、`vb_gate.py:22`、`vb_handoff.py:20`、`assets/AGENTS.block.md:1` 均为 `0.1.0`（POC），而来源分支名为 `v0.1.1` 且包含 R4–R8 修复 | 中 | 发版时统一定版本号（改动会影响注入块 marker 与测试，需单独提交） |
| V2 | 版本/哈希命名 | `SKILL.md:12` `standard_vendored_sha256` 实为 ZIP 包哈希，不是目录/清单哈希；可信判据是 `vb_trust.py` 的 `PINNED_MANIFEST_SHA256`（见 VENDOR-PROVENANCE.md） | 低 | 改名或补注释（改 frontmatter 字段需 Owner 确认） |
| V3 | 本机措辞 | `vibecoding/README.md:16`、`references/06-platform-capabilities.md:22-23,35-52` 用"本机"描述作者环境观测 | 低 | 改为"作者环境观测（日期）" |
| I1 | 干净机器安装 | 安装命令已改为仓库根 `python tools/install_skill.py ...`（`vibecoding/README.md:18-25`）；开发自测在临时目录完成安装、重复安装幂等（见 HANDOFF R9 段）。**未**在另一台真正干净的机器/非 Windows 系统上跑 | 中 | 公开前在 Linux/macOS 干净环境复跑 |
| I2 | 重装 | 安装器不删除文件，源中删除的文件在目标残留（设计如此，`tools/install_skill.py` 文档串）；无卸载命令 | 低 | 文档补卸载说明或提供卸载脚本 |
| A1 | 自动激活范围 | `SKILL.md:3` description 很宽（"starting or resuming development work in a repository"），可能在任何仓库被宿主自动激活；`vibecoding/README.md:47` 已声明"不保证激活"；`README.md:78`/`06-platform-capabilities.md:41,52` Cursor/WorkBuddy 自动激活 NOT_RUN | 中 | 公开前收窄 description 或明确说明激活范围 |

| R9-a | 换行策略 | 已加 `.gitattributes`（`* text=auto eol=lf`，`vibecoding/vendor/** -text`，R9-F2）；公开前确认所有贡献者/平台遵守，vendor 字节必须原样 | 中 | 保持；CI 中加 vb_trust 检查 |
| R9-b | 仓库入口 | 仓库根无 `README.md`（说明在 `vibecoding/README.md`） | 中 | 公开前加根 README |
| R9-c | Actions | 仓库 Actions 启用、allowed_actions=all，但无 workflow | 中 | Owner 决定：加 CI workflow 或收紧/关闭 Actions |
| R9-d | 私有评审痕迹 | `TODO.md`、`HANDOFF.md`、`OPEN_SOURCE_PREP.md` 含 R4–R10 评审 ID 与内部提交 SHA | 中 | 公开前精简或移出（同 P1） |
| R9-e | 中断恢复 | 恢复需“加 --force 重跑”（R9-F4 已更正文档）；无跨文件原子性，中断后残留部分文件 | 低 | 公开文档保留该说明 |
| R9-f | 再分发许可 | 需 Standard 所有者书面确认允许随技能再分发 vendor 副本（同 L2） | 阻断公开 | Owner 决定 |
| R9-g | 卸载 | 无卸载说明/命令（同 I2）：手工删除目标技能目录（含 `.vibecoding-install.json`）即可；项目内 `.vibecoding/` 与 AGENTS 注入块需手工移除 | 低 | 公开前写入 README |

## 已在本轮修复的平凡问题

- 拆仓导致的路径/命令：`AGENTS.md`、`vibecoding/README.md` 安装命令、`TODO.md` 路径说明、`tests/test_install_skill.py` 文档串（提交 2550597）。
- `AGENTS.md` 指向不存在的 `vendor/vibecoding-standard/VENDORED.md` → 改为 `vibecoding/vendor/VENDORED.md`（提交 2550597）。

## 未做

- 未改任何许可、身份、历史；未改 vendor；未做公开、Tag、Release。
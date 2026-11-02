# VENDOR-PROVENANCE — vendored Vibecoding Standard v1.2.8 来源与可复核证明

本文件位于 vendor 目录**之外**，不属于 38 文件副本本身；vendor 目录内不得编辑。

## 身份

| 项 | 值 |
|---|---|
| 标准版本 | 1.2.8 |
| 签收提交（Owner 签收的工程提交） | `2e010b04059172b651c191bf1dbaab279c8d78be` |
| 签收 Tree | `1e6c4e65f148353c851318a43cb98846250e8823` |
| 发布提交 / Tag | **PENDING**（尚未发布；工程候选 SHA 不得冒充发布 Commit） |
| 来源 | `git archive 2e010b0`（从 Standard 本地仓库直接导出，非发布 ZIP） |
| 发布 ZIP SHA-256 | **PENDING**（不以本地构建 ZIP 冒充） |
| `MANIFEST.sha256` 的 SHA-256（可信判据） | `ac261bc2bf03b5066070eddf01bf14e9ce10d0b29caaaff10dee8064e50608cd` |
| 文件数 | 38（37 登记文件 + `MANIFEST.sha256`） |
| 位置 | `vibecoding/vendor/vibecoding-standard/` |

注：`vibecoding/SKILL.md` frontmatter 的 `standard_vendored_sha256` 指发布 **ZIP 包**哈希；v1.2.8 尚无发布包，值为 `PENDING`。

## 信任模型（R4-N7）

`vibecoding/scripts/vb_trust.py` 内置 `PINNED_MANIFEST_SHA256`；先核对 `MANIFEST.sha256` 本身等于该值，再逐文件核对清单哈希、缺失与未登记文件。它**不执行**被校验目录内的任何代码。vendor 自带的 `tools/verify_manifest.py` 只能证明“目录与其自带清单自洽”，不能证明是签收版本。

运行时只信任上面的 v1.2.8 固定值。`vb_trust.LEGACY_MANIFEST_SHA256["1.2.7"]` 仅用于**识别**旧 vendor 以便提示升级（LEGACY_DETECTED），识别到旧版一律拒绝（退出码 1），不存在两个版本同时可信的运行路径。

## 复核命令（在仓库根执行）

```bash
python vibecoding/scripts/vb_trust.py vibecoding/vendor/vibecoding-standard
# 期望：== 可信校验: PASS（固定清单 v1.2.8；通过 37 / 失败 0 / 缺失 0 / 未登记 0）==，退出码 0
git ls-tree -r HEAD -- vibecoding/vendor/vibecoding-standard            # 与下表 blob 对照
git -C <Vibecoding-Standard> ls-tree -r 2e010b0
```

## 与签收提交 2e010b0 的 blob 对照

生成时结果：本仓库 38 个 / 来源 38 个；不一致 0，来源有而本仓库缺 0。

| 路径（相对 vendor/vibecoding-standard/） | blob SHA-1 | 与 2e010b0 |
|---|---|---|
| `.gitattributes` | `45ab7847aec6bcb6abb4381917c84f68e993635c` | = |
| `AI_PROJECT_STANDARD.md` | `31d2378484ba74aaeb9caa44e44c1e54297be678` | = |
| `CHANGELOG.md` | `53b2cbdc5eb5819057f2201ed4a6358ebc7b6155` | = |
| `COPYRIGHT-CHECKLIST.md` | `68137e4adc562175be5549b4d5170219c401d014` | = |
| `LICENSE-DRAFT.md` | `ddd859cf3501f2f6bade6f56298dc8108d85df67` | = |
| `MANIFEST.sha256` | `c1064c16c39451adbf237e9543b89df8d85cfa66` | = |
| `README.md` | `3fa3e69c90f3d0020c96fb6e3b5982b8205160a9` | = |
| `SECURITY.md` | `4671273c67454443a53553e2425ce9b05b949c2d` | = |
| `VERSION` | `4f2ea8d7e5ad18bc2a03b9b934f6635381ec0659` | = |
| `agents/Claude-Code.md` | `0316535275031b06fbe25c84a1b5a0a05b27dc43` | = |
| `agents/Codex.md` | `35da6227091da43b4e2071bdd07d1c161560e46b` | = |
| `docs/Agent接入指南.md` | `3427ffe8c39b42c5cb0c169595f323910273d6e0` | = |
| `templates/ADR-template.md.template` | `feeee2cd84837fb95e4b2f53fbc25408b0d4b19f` | = |
| `templates/AGENTS.md.template` | `5adc32dbf5276a9901568e262500139becea53d4` | = |
| `templates/CLAUDE.md.template` | `504e6eaa190f7a7ff17ad819dfb8cfb6285974cb` | = |
| `templates/DESIGN.md.template` | `ede90875bd9468c3f0ad7f1a2da061ae40ece541` | = |
| `templates/EVIDENCE-template.md.template` | `7457c1c197840855f093c19928348f137d5a60c1` | = |
| `templates/HANDOFF.md.template` | `550592de2b60ce81fecb2d4046e785ab618ea0a0` | = |
| `templates/PROGRESS.md.template` | `cdf5b9c48c303bef81060b4ab0186e39ab639da8` | = |
| `templates/README.md` | `b82764d27a1333ceb72b667d7a2486348bcaf679` | = |
| `templates/README.md.template` | `d8e7f1e8f4e9276f631ae8d84e19c87fd25530f9` | = |
| `templates/ROADMAP.md.template` | `1b442a482c67735f5c367146a5817028584f24e1` | = |
| `templates/SPEC-template.md.template` | `9ce4a98c978564efd55eb0f8fd481bc2bf4933af` | = |
| `templates/STATUS.md.template` | `58e3a36be4f232903feb99872a5fc3e7b67cbecb` | = |
| `templates/TODO.md.template` | `eca9b789ef086f52803601b3db7196283c0be023` | = |
| `templates/TRACEABILITY.md.template` | `cdf8faa3eb0fbb1c7f86a1c55541c7b942ad0409` | = |
| `templates/architecture.md.template` | `af9b6f02bd635c3eb17c014edfb486f6736bfbf3` | = |
| `templates/component-api.md.template` | `c51e7409be5f016f586e36ea6a10e06e0187c6a5` | = |
| `templates/development.md.template` | `5ccf14a2e1138735e80b92605524efb2303140cc` | = |
| `templates/project-overview.md.template` | `73c9d600e0afdd3ecb7f7475c7094a2ed7c81843` | = |
| `templates/user-guide.md.template` | `67202f9a75f0bb6e8d856fc1bab987b9d3b5c94b` | = |
| `tests/test_tools.py` | `a73a723cb3e8d15a16348d725e159c07096e1e1e` | = |
| `tools/check_evidence.py` | `186a1b9840f79a16628b2305af9c8a5939de0b93` | = |
| `tools/check_links.py` | `26a389e0411077a37e1f501ce6aaaeaa25b4bf08` | = |
| `tools/release_zip.py` | `207720080bfb0ee0aa694e460dc1a9098cabd43d` | = |
| `tools/update_manifest.py` | `9ef18a8e8fac858944ac0d2c5b4035395fc57577` | = |
| `tools/verify_manifest.py` | `4b61134bf528c300d6e6d2b9363b271a91bf84b4` | = |
| `完整任务示例.md` | `3330508c3e8423def5fc718f78d9ace9f9c26992` | = |

## 历史

- v1.2.7（签收 `ce5b361…`，发布 `fd9750f…`，ZIP `0ce2a06c…`，MANIFEST `68d8a834…`，34 文件）：已被 S-SKILL-01 整体替换；身份常量仅保留于 `vb_init.LEGACY_IDENTITIES` 与 `vb_trust.LEGACY_MANIFEST_SHA256`，用于升级识别。

## 有意变更：vendor 换行属性（R10 测试口径调整，Owner 批准方案 a）

- 原因：v1.2.8 签收树自带 `vibecoding/vendor/vibecoding-standard/.gitattributes`（固定清单条目，SHA-256 `dad26b22b8924c9d87fb0379dc758a6c5d7ebf2986e5f6ffeeb5ed416bf3689f`，不可删改），内容为 `* text=auto eol=lf` 与 `*.zip binary`。按 git 就近优先规则，它覆盖根目录 `vibecoding/vendor/** -text`，vendor 文件的 `text` 属性由 `unset` 变为 `auto`。
- 证据：S-SKILL-01 首轮 WSL（Ubuntu / Python 3.10.6 / git 2.34.1）`test_vb_gate.TestR10GitAttributes.test_check_attr` **FAIL**（期望 `text: unset`，实得 `text: auto` / `eol: lf`）；同一测试在 cfc083d 基线 WSL 通过。首轮 Windows 三个 Python（3.14 / 3.12 / 3.10）中该测试为 **SKIP（非 PASS）**：旧实现以 `.git` 是否为目录判定检出，worktree 中 `.git` 为文件，故跳过。
- 决议：Owner 批准方案 a——测试改为断言字节一致性的实际保障：全部 vendor 文件 `eol: lf`、vendor 文件不含任何 CR 字节、`*.zip` 为 `binary`（`text`/`diff` unset）；根规则 `tools/install_skill.py: text auto / eol lf` 断言保留。
- 检出判定改为 `git rev-parse --is-inside-work-tree`，worktree 中实际运行（不再 SKIP）；`check-attr -z` 避免中文路径被 quotePath 转义。
- 实测：38 个 vendor 文件 0 个含 CR、全部可按 UTF-8 解码。残余：若上游将来加入含 CRLF 的文本文件，`text=auto` 会在提交时规范化；由固定清单 SHA-256 校验兜底发现。
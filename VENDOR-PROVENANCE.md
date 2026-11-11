# VENDOR-PROVENANCE — vendored Vibecoding Standard v1.2.9 来源与可复核证明

本文件位于 vendor 目录**之外**，不属于 39 文件副本本身；vendor 目录内不得编辑。

## 身份

| 项 | 值 |
|---|---|
| 标准版本 | 1.2.9 |
| 签收提交（工程候选） | `2e010b04059172b651c191bf1dbaab279c8d78be` |
| 发布提交 / Tag | `b1ece9f5743d4330524da7b813f6852b7cbc75ad` / `v1.2.9` |
| 发布 Tree | `1ec8875114fe45c2da4303c1de79069866bcd1b6` |
| 来源 | `git archive b1ece9f`（与 GitHub Release ZIP 同源） |
| 发布 ZIP SHA-256 | `ddaba6788a79f61abf570e886b515fd318d67ace87d3cce73f08204818471946` |
| `MANIFEST.sha256` 的 SHA-256（可信判据） | `46035ee2c0d0063564a3215ea411f80d51ce0d18088a6cda879f525f9e9ec19e` |
| 文件数 | 39（38 登记文件 + `MANIFEST.sha256`） |
| 位置 | `vibecoding/vendor/vibecoding-standard/` |
| 许可 | MIT（Copyright (c) 2026 YunAbove）；见 vendor 内 `LICENSE` |

注：`vibecoding/SKILL.md` frontmatter 的 `standard_vendored_sha256` 为发布 **ZIP 包**哈希。

## 信任模型（R4-N7）

`vibecoding/scripts/vb_trust.py` 内置 `PINNED_MANIFEST_SHA256`；先核对 `MANIFEST.sha256` 本身等于该值，再逐文件核对清单哈希、缺失与未登记文件。它**不执行**被校验目录内的任何代码。vendor 自带的 `tools/verify_manifest.py` 只能证明“目录与其自带清单自洽”，不能证明是签收/发布版本。

运行时只信任上面的 v1.2.9 固定值。`LEGACY_MANIFEST_SHA256` 中的 `1.2.7` / `1.2.8` 仅用于识别旧 vendor（LEGACY_DETECTED）。

## 复核命令（在仓库根执行）

```bash
python vibecoding/scripts/vb_trust.py vibecoding/vendor/vibecoding-standard
git ls-tree -r HEAD -- vibecoding/vendor/vibecoding-standard
git -C <Vibecoding-Standard> ls-tree -r b1ece9f
```

## 与发布提交 b1ece9f 的 blob 对照

生成时结果：本仓库 39 个；与来源不一致 0，来源缺失 0。

| 路径（相对 vendor/vibecoding-standard/） | blob SHA-1 | 与发布 tip |
|---|---|---|
| `.gitattributes` | `45ab7847aec6bcb6abb4381917c84f68e993635c` | = |
| `AI_PROJECT_STANDARD.md` | `4765343b8147bcb738a1cf51608846a45164b7b8` | = |
| `CHANGELOG.md` | `92efe4fcd382bbb689ef0ffcf94a693ef2ef95c8` | = |
| `COPYRIGHT-CHECKLIST.md` | `ca21a980e71be41aaaf4f310774bad214f513ef2` | = |
| `LICENSE` | `0353a4d850a2c7c3ddd5f2e23f448b53253ba106` | = |
| `LICENSE-DRAFT.md` | `d01a527d781fc303a7e0113f8dc5569649d2bd0d` | = |
| `MANIFEST.sha256` | `e1550f0c12545426aadf4566d002c27fea027977` | = |
| `README.md` | `6967a9b68321354ee0ba90a667dbcbe7849d2bf4` | = |
| `SECURITY.md` | `4671273c67454443a53553e2425ce9b05b949c2d` | = |
| `VERSION` | `9d4f8239dc9c87dcec48f0b9631e72ddbfbae9e5` | = |
| `agents/Claude-Code.md` | `11608248a88193b95dc5ef8c567b367950626c7a` | = |
| `agents/Codex.md` | `2d492e8f4802b15ba974a2a4f5297ac848e07879` | = |
| `docs/Agent接入指南.md` | `2eccd2479b806b9d61fe624325b0839743fa10a5` | = |
| `templates/ADR-template.md.template` | `feeee2cd84837fb95e4b2f53fbc25408b0d4b19f` | = |
| `templates/AGENTS.md.template` | `8a6e5058594c58572c545d5a520de16242e001d8` | = |
| `templates/CLAUDE.md.template` | `504e6eaa190f7a7ff17ad819dfb8cfb6285974cb` | = |
| `templates/DESIGN.md.template` | `ede90875bd9468c3f0ad7f1a2da061ae40ece541` | = |
| `templates/EVIDENCE-template.md.template` | `7457c1c197840855f093c19928348f137d5a60c1` | = |
| `templates/HANDOFF.md.template` | `550592de2b60ce81fecb2d4046e785ab618ea0a0` | = |
| `templates/PROGRESS.md.template` | `cdf5b9c48c303bef81060b4ab0186e39ab639da8` | = |
| `templates/README.md` | `4636635dce422d92c7d4096a2b2b3641d3345076` | = |
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

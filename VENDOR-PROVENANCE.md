# VENDOR-PROVENANCE — vendored Vibecoding Standard v1.2.8 来源与可复核证明

本文件位于 vendor 目录**之外**，不属于 38 文件副本本身；vendor 目录内不得编辑。

## 身份

| 项 | 值 |
|---|---|
| 标准版本 | 1.2.8 |
| 签收提交（工程候选） | `2e010b04059172b651c191bf1dbaab279c8d78be` |
| 发布提交 / Tag | `d9abf273ff3ee7afebf39541c7a031922e1bb5be` / `v1.2.8` |
| 发布 Tree | `d21d9d1dfef7bffb2e672aea57b2da0bf09d1899` |
| 来源 | `git archive d9abf27`（与私有正式 ZIP 同源） |
| 发布 ZIP SHA-256 | `6f3ca956f942e219bbc3dca62ca58e570a701ffee8a1726721483f9993aa54df` |
| `MANIFEST.sha256` 的 SHA-256（可信判据） | `28303d4c5548bf3d464c5e70c04e607da7e58645c0e3904f9c4c52202e88304c` |
| 文件数 | 38（37 登记文件 + `MANIFEST.sha256`） |
| 位置 | `vibecoding/vendor/vibecoding-standard/` |
| 许可 | 私有正式发布；`LICENSE-DRAFT` 未授予开源许可 |

注：`vibecoding/SKILL.md` frontmatter 的 `standard_vendored_sha256` 为发布 **ZIP 包**哈希。

## 信任模型（R4-N7）

`vibecoding/scripts/vb_trust.py` 内置 `PINNED_MANIFEST_SHA256`；先核对 `MANIFEST.sha256` 本身等于该值，再逐文件核对清单哈希、缺失与未登记文件。它**不执行**被校验目录内的任何代码。vendor 自带的 `tools/verify_manifest.py` 只能证明“目录与其自带清单自洽”，不能证明是签收/发布版本。

运行时只信任上面的 v1.2.8 固定值。`LEGACY_MANIFEST_SHA256["1.2.7"]` 仅用于识别旧 vendor（LEGACY_DETECTED）。

## 复核命令（在仓库根执行）

```bash
python vibecoding/scripts/vb_trust.py vibecoding/vendor/vibecoding-standard
git ls-tree -r HEAD -- vibecoding/vendor/vibecoding-standard
git -C <Vibecoding-Standard> ls-tree -r d9abf27
```

## 与发布提交 d9abf27 的 blob 对照

生成时结果：本仓库 38 个；与来源不一致 0，来源缺失 0。

| 路径（相对 vendor/vibecoding-standard/） | blob SHA-1 | 与发布 tip |
|---|---|---|
| `.gitattributes` | `45ab7847aec6bcb6abb4381917c84f68e993635c` | = |
| `AI_PROJECT_STANDARD.md` | `f8f0f74fcb9aaeca14ff4dfff743a0f5e236eb6c` | = |
| `CHANGELOG.md` | `af04b1ba3acabdf9a8af701b889bd76817baf170` | = |
| `COPYRIGHT-CHECKLIST.md` | `68137e4adc562175be5549b4d5170219c401d014` | = |
| `LICENSE-DRAFT.md` | `ddd859cf3501f2f6bade6f56298dc8108d85df67` | = |
| `MANIFEST.sha256` | `1bae34f900ad8b0fe534ab9c4b3e73450325eec0` | = |
| `README.md` | `cbc3d9ba463be0fca05fa6fdebfc110edd102212` | = |
| `SECURITY.md` | `4671273c67454443a53553e2425ce9b05b949c2d` | = |
| `VERSION` | `db6fb4a9113767d50f4a5027af3423a5d383dd55` | = |
| `agents/Claude-Code.md` | `ad93abe6e1b138b27d1314adbc05056fdd7d5a4c` | = |
| `agents/Codex.md` | `c8ba56c17ffd41b01e37b815332829264b12a70a` | = |
| `docs/Agent接入指南.md` | `acb88e9c7b698c9f67b0c06a95f9445f330f7a27` | = |
| `templates/ADR-template.md.template` | `feeee2cd84837fb95e4b2f53fbc25408b0d4b19f` | = |
| `templates/AGENTS.md.template` | `fa00595002d492ba6571fff019b9c8533b22642a` | = |
| `templates/CLAUDE.md.template` | `504e6eaa190f7a7ff17ad819dfb8cfb6285974cb` | = |
| `templates/DESIGN.md.template` | `ede90875bd9468c3f0ad7f1a2da061ae40ece541` | = |
| `templates/EVIDENCE-template.md.template` | `7457c1c197840855f093c19928348f137d5a60c1` | = |
| `templates/HANDOFF.md.template` | `550592de2b60ce81fecb2d4046e785ab618ea0a0` | = |
| `templates/PROGRESS.md.template` | `cdf5b9c48c303bef81060b4ab0186e39ab639da8` | = |
| `templates/README.md` | `2720561ce658ce04a53ee631ba9ad1192869e77b` | = |
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


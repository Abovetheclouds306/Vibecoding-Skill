# VENDOR-PROVENANCE — vendored Vibecoding Standard v1.2.7 来源与可复核证明

本文件位于 vendor 目录**之外**，不属于 34 文件副本本身；vendor 目录内不得编辑。

## 身份

| 项 | 值 |
|---|---|
| 标准版本 | 1.2.7（Tag `v1.2.7`） |
| 签收提交 | `ce5b361cf13ae373094abe67eb9ce7a6e22ecb8f` |
| 发布提交（merge） | `fd9750f3e6c4c2105cf253d5f7d6494f0f373fdf` |
| 发布 Tree | `bef80258b5bb7f4b8de69ea1a7590ab4f1a129c1` |
| 来源包 | `vibecoding-standard-v1.2.7-ce5b361.zip`，**ZIP 文件** SHA-256 `0ce2a06cf506904cca4e0597240d43f5e869ee9845d7b508bc83a9fd2745dd38` |
| `MANIFEST.sha256` 的 SHA-256（可信判据） | `68d8a834eaab9b0106bfa2dbc651bf9f67daee848f28262230140ac958ff6cd0` |
| 文件数 | 34（33 登记文件 + `MANIFEST.sha256`） |
| 位置 | `vibecoding/vendor/vibecoding-standard/` |

注：`vibecoding/SKILL.md` frontmatter 的 `standard_vendored_sha256` 值为上面的 **ZIP 包**哈希，不是目录或清单哈希（命名易误解，见 OPEN_SOURCE_PREP.md）。

## 信任模型（R4-N7）

`vibecoding/scripts/vb_trust.py` 内置 `PINNED_MANIFEST_SHA256`；先核对 `MANIFEST.sha256` 本身等于该值，再逐文件核对清单哈希、缺失与未登记文件。它**不执行**被校验目录内的任何代码。vendor 自带的 `tools/verify_manifest.py` 只能证明“目录与其自带清单自洽”，不能证明是签收版本。

## 复核命令（在仓库根执行）

```bash
python vibecoding/scripts/vb_trust.py vibecoding/vendor/vibecoding-standard
# 期望：== 可信校验: PASS（固定清单 v1.2.7；通过 33 / 失败 0 / 缺失 0 / 未登记 0）==，退出码 0
python vibecoding/vendor/vibecoding-standard/tools/verify_manifest.py   # 自洽性（辅助）
git ls-tree -r HEAD -- vibecoding/vendor/vibecoding-standard            # 与下表 blob 对照
git -C <Vibecoding-Standard> ls-tree -r 53eb3917765a45582034a0af7f1ae33a7342c3b9 skill/vibecoding/vendor/vibecoding-standard
```

## 与来源候选 53eb391 的 blob 对照

生成时结果：本仓库 34 个 / 来源 34 个；不一致 0，来源有而本仓库缺 0。（来源 blob 取自 `PROVENANCE.md`，其值由 `git ls-tree 53eb391` 得出。）

| 路径（相对 vendor/vibecoding-standard/） | blob SHA-1 | 与 53eb391 |
|---|---|---|
| `AI_PROJECT_STANDARD.md` | `97d748efebd01b87588a44c8e72cc719100dee91` | = |
| `CHANGELOG.md` | `275aadba64078207c796943d07d830bfc0a23e31` | = |
| `MANIFEST.sha256` | `2ca02ec2cfdc35b6ad474d5b7f614f74e3ddb099` | = |
| `README.md` | `f662d56f1dbd625cbd300b4df4f72f0cd11378c6` | = |
| `agents/Claude-Code.md` | `b676a934ed3102b09de74fe57f23263954a53929` | = |
| `agents/Codex.md` | `5bcbc316e24efd62689ec1b6463c544845abf00a` | = |
| `docs/Agent接入指南.md` | `6641a6e8ee38be1c62fc2c99378340c212536434` | = |
| `docs/候选优化报告-v1.2.7.md` | `2ad71a16f03314ab425821bc882561ad991c7091` | = |
| `templates/ADR-template.md.template` | `feeee2cd84837fb95e4b2f53fbc25408b0d4b19f` | = |
| `templates/AGENTS.md.template` | `a761200e3d533d2490e1fcc027230b888391f182` | = |
| `templates/CLAUDE.md.template` | `bd8c1cf3f1f2a150154d2f4951b6ed401713e9d1` | = |
| `templates/DESIGN.md.template` | `ede90875bd9468c3f0ad7f1a2da061ae40ece541` | = |
| `templates/EVIDENCE-template.md.template` | `7457c1c197840855f093c19928348f137d5a60c1` | = |
| `templates/HANDOFF.md.template` | `550592de2b60ce81fecb2d4046e785ab618ea0a0` | = |
| `templates/PROGRESS.md.template` | `cdf5b9c48c303bef81060b4ab0186e39ab639da8` | = |
| `templates/README.md` | `4664acc612d14b8b94eb9c1ad1c272ce822ad407` | = |
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
| `tests/test_tools.py` | `75955ec78337f478b2a09da559a7c4b1fd247857` | = |
| `tools/check_evidence.py` | `dbd5f3a479aa70815719865d24b7909e3d945c72` | = |
| `tools/check_links.py` | `26a389e0411077a37e1f501ce6aaaeaa25b4bf08` | = |
| `tools/release_zip.py` | `207720080bfb0ee0aa694e460dc1a9098cabd43d` | = |
| `tools/update_manifest.py` | `9ef18a8e8fac858944ac0d2c5b4035395fc57577` | = |
| `tools/verify_manifest.py` | `4b61134bf528c300d6e6d2b9363b271a91bf84b4` | = |
| `完整任务示例.md` | `57df1aee9167d25072b167604999408c2c7bd362` | = |

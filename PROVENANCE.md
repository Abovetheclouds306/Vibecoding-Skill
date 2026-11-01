# PROVENANCE — 来源映射

本仓库由 Vibecoding-Standard 私有仓库中的 Skill 冻结候选**原样提取**（不重新实现，不复制原仓库历史）。

| 项 | 值 |
|---|---|
| 来源仓库 | `Abovetheclouds306/Vibecoding-Standard`（私有） |
| 来源分支 | `fix/skill-ins1-cli-v0.1.1` |
| 来源完整 SHA | `53eb3917765a45582034a0af7f1ae33a7342c3b9` |
| 来源子树 | `skill/`（新仓库根 = 原 `skill/`） |
| 原 POC 基线 | `c08407d6a779124efff295cf4716400fbd7c6786` |
| Vendor | Vibecoding Standard v1.2.7，签收提交 `ce5b361cf13ae373094abe67eb9ce7a6e22ecb8f`，34 文件逐字节副本（见 `VENDOR-PROVENANCE.md` 之后续提交） |

初始提交中每个文件的 Git blob 与来源树逐一相等。复核：

```
git -C <Vibecoding-Standard> ls-tree -r 53eb3917765a45582034a0af7f1ae33a7342c3b9 skill
git ls-tree -r <初始提交> -- . ':!PROVENANCE.md'
```

## 文件映射（新路径 → 来源路径 · blob SHA-1）

| 新路径 | 来源路径 | blob |
|---|---|---|
| `AGENTS.md` | `skill/AGENTS.md` | `a70d65c43028c34dcc89377de74e599499008a89` |
| `HANDOFF.md` | `skill/HANDOFF.md` | `af18996effd9c3c5685056b27a54a0498bb28fe6` |
| `TODO.md` | `skill/TODO.md` | `beb46df8d1e0b4fd4be1110d14641e934ecccc4a` |
| `tests/test_install_skill.py` | `skill/tests/test_install_skill.py` | `af553c80aa1ee2ab47c5be9f956e6c1ee3d49210` |
| `tests/test_vb_init.py` | `skill/tests/test_vb_init.py` | `c8dcc490250dc099ce23740d9b910ad2bbcb0221` |
| `tests/test_vb_init_cli.py` | `skill/tests/test_vb_init_cli.py` | `2740adbcea3caf881d2826b0aecff83b022ebe15` |
| `tools/install_skill.py` | `skill/tools/install_skill.py` | `18893ae001646b02baa5a5bbc1e511cc2f0cb941` |
| `vibecoding/README.md` | `skill/vibecoding/README.md` | `e46ce20ba5cc71848b2f9c07da4c6504085a7399` |
| `vibecoding/SKILL.md` | `skill/vibecoding/SKILL.md` | `246e93a555368f72feabbe1614ea8c1b18050045` |
| `vibecoding/assets/AGENTS.block.md` | `skill/vibecoding/assets/AGENTS.block.md` | `d180e8da29b08479f9c046b5a4e67841a507757b` |
| `vibecoding/references/01-project-init.md` | `skill/vibecoding/references/01-project-init.md` | `b84e24d63ca203555e9a559fd6b221860fdf06f1` |
| `vibecoding/references/02-existing-rules.md` | `skill/vibecoding/references/02-existing-rules.md` | `ccadbd54f87e0a0add81936925af11eba8b1262d` |
| `vibecoding/references/03-task-flow.md` | `skill/vibecoding/references/03-task-flow.md` | `be49872f1e99751be6e6cdd43f900f77a7cc07f5` |
| `vibecoding/references/04-evidence-gate.md` | `skill/vibecoding/references/04-evidence-gate.md` | `5cd9a9b3f59d2c730b7c4419ea24c5eeb67b1057` |
| `vibecoding/references/05-handoff.md` | `skill/vibecoding/references/05-handoff.md` | `3bcc560dcf22d9934fe9129d827d667ff9b8a6f0` |
| `vibecoding/references/06-platform-capabilities.md` | `skill/vibecoding/references/06-platform-capabilities.md` | `c04787e4c3b75da2bac5e459084970f8bb896cb0` |
| `vibecoding/scripts/vb_gate.py` | `skill/vibecoding/scripts/vb_gate.py` | `b3998a5f08333d7c65e2b27385c3b87a9419aab2` |
| `vibecoding/scripts/vb_handoff.py` | `skill/vibecoding/scripts/vb_handoff.py` | `dda1958cd8386852b0a19d5e3df626db615088f8` |
| `vibecoding/scripts/vb_init.py` | `skill/vibecoding/scripts/vb_init.py` | `15fa2239e69bd11dc20a890134ad3a63f2fcc7d7` |
| `vibecoding/vendor/VENDORED.md` | `skill/vibecoding/vendor/VENDORED.md` | `d83c1031b082482126990f33157a183fb1545ba2` |
| `vibecoding/vendor/vibecoding-standard/AI_PROJECT_STANDARD.md` | `skill/vibecoding/vendor/vibecoding-standard/AI_PROJECT_STANDARD.md` | `97d748efebd01b87588a44c8e72cc719100dee91` |
| `vibecoding/vendor/vibecoding-standard/CHANGELOG.md` | `skill/vibecoding/vendor/vibecoding-standard/CHANGELOG.md` | `275aadba64078207c796943d07d830bfc0a23e31` |
| `vibecoding/vendor/vibecoding-standard/MANIFEST.sha256` | `skill/vibecoding/vendor/vibecoding-standard/MANIFEST.sha256` | `2ca02ec2cfdc35b6ad474d5b7f614f74e3ddb099` |
| `vibecoding/vendor/vibecoding-standard/README.md` | `skill/vibecoding/vendor/vibecoding-standard/README.md` | `f662d56f1dbd625cbd300b4df4f72f0cd11378c6` |
| `vibecoding/vendor/vibecoding-standard/agents/Claude-Code.md` | `skill/vibecoding/vendor/vibecoding-standard/agents/Claude-Code.md` | `b676a934ed3102b09de74fe57f23263954a53929` |
| `vibecoding/vendor/vibecoding-standard/agents/Codex.md` | `skill/vibecoding/vendor/vibecoding-standard/agents/Codex.md` | `5bcbc316e24efd62689ec1b6463c544845abf00a` |
| `vibecoding/vendor/vibecoding-standard/docs/Agent接入指南.md` | `skill/vibecoding/vendor/vibecoding-standard/docs/Agent接入指南.md` | `6641a6e8ee38be1c62fc2c99378340c212536434` |
| `vibecoding/vendor/vibecoding-standard/docs/候选优化报告-v1.2.7.md` | `skill/vibecoding/vendor/vibecoding-standard/docs/候选优化报告-v1.2.7.md` | `2ad71a16f03314ab425821bc882561ad991c7091` |
| `vibecoding/vendor/vibecoding-standard/templates/ADR-template.md.template` | `skill/vibecoding/vendor/vibecoding-standard/templates/ADR-template.md.template` | `feeee2cd84837fb95e4b2f53fbc25408b0d4b19f` |
| `vibecoding/vendor/vibecoding-standard/templates/AGENTS.md.template` | `skill/vibecoding/vendor/vibecoding-standard/templates/AGENTS.md.template` | `a761200e3d533d2490e1fcc027230b888391f182` |
| `vibecoding/vendor/vibecoding-standard/templates/CLAUDE.md.template` | `skill/vibecoding/vendor/vibecoding-standard/templates/CLAUDE.md.template` | `bd8c1cf3f1f2a150154d2f4951b6ed401713e9d1` |
| `vibecoding/vendor/vibecoding-standard/templates/DESIGN.md.template` | `skill/vibecoding/vendor/vibecoding-standard/templates/DESIGN.md.template` | `ede90875bd9468c3f0ad7f1a2da061ae40ece541` |
| `vibecoding/vendor/vibecoding-standard/templates/EVIDENCE-template.md.template` | `skill/vibecoding/vendor/vibecoding-standard/templates/EVIDENCE-template.md.template` | `7457c1c197840855f093c19928348f137d5a60c1` |
| `vibecoding/vendor/vibecoding-standard/templates/HANDOFF.md.template` | `skill/vibecoding/vendor/vibecoding-standard/templates/HANDOFF.md.template` | `550592de2b60ce81fecb2d4046e785ab618ea0a0` |
| `vibecoding/vendor/vibecoding-standard/templates/PROGRESS.md.template` | `skill/vibecoding/vendor/vibecoding-standard/templates/PROGRESS.md.template` | `cdf5b9c48c303bef81060b4ab0186e39ab639da8` |
| `vibecoding/vendor/vibecoding-standard/templates/README.md` | `skill/vibecoding/vendor/vibecoding-standard/templates/README.md` | `4664acc612d14b8b94eb9c1ad1c272ce822ad407` |
| `vibecoding/vendor/vibecoding-standard/templates/README.md.template` | `skill/vibecoding/vendor/vibecoding-standard/templates/README.md.template` | `d8e7f1e8f4e9276f631ae8d84e19c87fd25530f9` |
| `vibecoding/vendor/vibecoding-standard/templates/ROADMAP.md.template` | `skill/vibecoding/vendor/vibecoding-standard/templates/ROADMAP.md.template` | `1b442a482c67735f5c367146a5817028584f24e1` |
| `vibecoding/vendor/vibecoding-standard/templates/SPEC-template.md.template` | `skill/vibecoding/vendor/vibecoding-standard/templates/SPEC-template.md.template` | `9ce4a98c978564efd55eb0f8fd481bc2bf4933af` |
| `vibecoding/vendor/vibecoding-standard/templates/STATUS.md.template` | `skill/vibecoding/vendor/vibecoding-standard/templates/STATUS.md.template` | `58e3a36be4f232903feb99872a5fc3e7b67cbecb` |
| `vibecoding/vendor/vibecoding-standard/templates/TODO.md.template` | `skill/vibecoding/vendor/vibecoding-standard/templates/TODO.md.template` | `eca9b789ef086f52803601b3db7196283c0be023` |
| `vibecoding/vendor/vibecoding-standard/templates/TRACEABILITY.md.template` | `skill/vibecoding/vendor/vibecoding-standard/templates/TRACEABILITY.md.template` | `cdf8faa3eb0fbb1c7f86a1c55541c7b942ad0409` |
| `vibecoding/vendor/vibecoding-standard/templates/architecture.md.template` | `skill/vibecoding/vendor/vibecoding-standard/templates/architecture.md.template` | `af9b6f02bd635c3eb17c014edfb486f6736bfbf3` |
| `vibecoding/vendor/vibecoding-standard/templates/component-api.md.template` | `skill/vibecoding/vendor/vibecoding-standard/templates/component-api.md.template` | `c51e7409be5f016f586e36ea6a10e06e0187c6a5` |
| `vibecoding/vendor/vibecoding-standard/templates/development.md.template` | `skill/vibecoding/vendor/vibecoding-standard/templates/development.md.template` | `5ccf14a2e1138735e80b92605524efb2303140cc` |
| `vibecoding/vendor/vibecoding-standard/templates/project-overview.md.template` | `skill/vibecoding/vendor/vibecoding-standard/templates/project-overview.md.template` | `73c9d600e0afdd3ecb7f7475c7094a2ed7c81843` |
| `vibecoding/vendor/vibecoding-standard/templates/user-guide.md.template` | `skill/vibecoding/vendor/vibecoding-standard/templates/user-guide.md.template` | `67202f9a75f0bb6e8d856fc1bab987b9d3b5c94b` |
| `vibecoding/vendor/vibecoding-standard/tests/test_tools.py` | `skill/vibecoding/vendor/vibecoding-standard/tests/test_tools.py` | `75955ec78337f478b2a09da559a7c4b1fd247857` |
| `vibecoding/vendor/vibecoding-standard/tools/check_evidence.py` | `skill/vibecoding/vendor/vibecoding-standard/tools/check_evidence.py` | `dbd5f3a479aa70815719865d24b7909e3d945c72` |
| `vibecoding/vendor/vibecoding-standard/tools/check_links.py` | `skill/vibecoding/vendor/vibecoding-standard/tools/check_links.py` | `26a389e0411077a37e1f501ce6aaaeaa25b4bf08` |
| `vibecoding/vendor/vibecoding-standard/tools/release_zip.py` | `skill/vibecoding/vendor/vibecoding-standard/tools/release_zip.py` | `207720080bfb0ee0aa694e460dc1a9098cabd43d` |
| `vibecoding/vendor/vibecoding-standard/tools/update_manifest.py` | `skill/vibecoding/vendor/vibecoding-standard/tools/update_manifest.py` | `9ef18a8e8fac858944ac0d2c5b4035395fc57577` |
| `vibecoding/vendor/vibecoding-standard/tools/verify_manifest.py` | `skill/vibecoding/vendor/vibecoding-standard/tools/verify_manifest.py` | `4b61134bf528c300d6e6d2b9363b271a91bf84b4` |
| `vibecoding/vendor/vibecoding-standard/完整任务示例.md` | `skill/vibecoding/vendor/vibecoding-standard/完整任务示例.md` | `57df1aee9167d25072b167604999408c2c7bd362` |

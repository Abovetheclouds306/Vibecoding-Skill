# 开发入口规则（Vibecoding Skill）

本文件只是入口与指针，**不是第二份规范**。

- 权威规范：`vibecoding/vendor/vibecoding-standard/`（vendored v1.2.7，来源与哈希见 `vibecoding/vendor/VENDORED.md` 与仓库根 `PROVENANCE.md`）。冲突时以 vendor 为准。
- vendor 目录只读：禁止修改 `vibecoding/vendor/**`；其可信判据是 `python vibecoding/scripts/vb_trust.py vibecoding/vendor/vibecoding-standard` PASS（固定 v1.2.7 清单 SHA-256）；vendor 自带 `tools/verify_manifest.py` 只证明自洽，不能作为可信依据。
- 任务真相源：`TODO.md`（待办与状态）、`HANDOFF.md`（最近一轮交接与证据）。本地 Git 状态是唯一事实。
- 测试：`python -m unittest discover -s tests -v`（仓库根目录）；测试只能用系统临时目录，禁止触碰真实技能安装目录。
- 开发者自测 ≠ 独立复核（R4）。结论标 PASS / FAIL / UNKNOWN / NOT_RUN。
- 禁止（除 Owner 另行明确授权；当前仅授权推送私有仓库 main）：push / merge / tag / release、reset / clean、弱化断言、新增功能或改变规范契约。

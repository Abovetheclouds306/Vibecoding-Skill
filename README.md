# Vibecoding Skill

把 Vibecoding Standard v1.2.9 的工程纪律打包成可安装的 Agent Skill（Claude Code / Codex / Cursor / WorkBuddy），提供项目初始化（`vb_init.py`）、验证证据门禁（`vb_gate.py`）与交接（`vb_handoff.py`）。状态：v0.1.0 POC。

## 安装

需要 Python 3.10+。在本仓库根目录执行（只复制 + 校验，不改系统配置；先 `--dry-run` 看计划）：

```bash
python tools/install_skill.py --target claude-code --scope project --project <项目> --dry-run
python tools/install_skill.py --target claude-code --scope project --project <项目>
```

`--target` 可选 `claude-code`、`codex`、`cursor`、`workbuddy`、`workbuddy-alt`；`--scope user` 安装到用户目录。更新已安装副本加 `--force`（只更新可确认归属的文件，不删除、不覆盖用户文件）。详见 [`vibecoding/README.md`](vibecoding/README.md)。

## 校验

```bash
python vibecoding/scripts/vb_trust.py vibecoding/vendor/vibecoding-standard
```

退出码 0（PASS）表示标准副本与固定的 v1.2.9 清单 SHA-256 一致。这是唯一的可信判据；标准副本自带的 `verify_manifest.py` 只是自洽性自检，不是信任根。

## 卸载

见 [`vibecoding/README.md` 第七节](vibecoding/README.md)：删除安装目标技能目录；如运行过 `vb_init.py --apply`，手工删除项目内 `.vibecoding/` 与 `AGENTS.md` 中的 vibecoding 标记块。

## 安全

见 [`SECURITY.md`](SECURITY.md)（信任根、`--python`/`--verify` 由调用者信任、临时目录与竞态边界、漏洞报告方式）。

## 许可

**MIT License**（Copyright (c) 2026 YunAbove）。见 [`LICENSE`](LICENSE)。  
vendored Standard 使用同一持有人的 MIT 许可，见 [`vibecoding/vendor/vibecoding-standard/LICENSE`](vibecoding/vendor/vibecoding-standard/LICENSE)。
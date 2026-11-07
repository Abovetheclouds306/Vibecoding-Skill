# Sanitized evidence snapshot — 2026-11-08

建议落仓路径：`docs/evidence/2026-11-08-windows-skill-integration/`。这是建议，未查询仓库是否已有相同目录规范。

## 来源及可信边界
`integration/`完整保留已交付45个文本文件（报告、16个命令日志、fixture、工具与哈希）；`independent/`含限定范围独立收尾JSON。读取证据不是重新运行测试。用户交互转录仅以归因摘要保留，没有独立原会话日志或人工签名。SUMMARY-ZH.md区分三段证据来源。

## 脱敏
Windows测试根绝对路径替换为 `<TEST_ROOT>`，其余用户目录为 `<USER_HOME>`，如出现设备标识则替换 `<MACHINE>`。保留项目相对路径、标准版本、任务ID、命令参数、输出、退出码、时间(+08:00 Asia/Shanghai)与原哈希。没有纳入邮箱/个人正文/凭据/应用配置。fixture自身config是测试产物而非用户登录配置。

历史报告中的哈希属于脱敏前字节：不可拿脱敏文件重新计算后与历史哈希判定原测试失败。`SANITIZED-SHA256SUMS`只校验本次脱敏payload字节；不证明作者、原会话真实性或脱敏前字节等价。原始输入整包SHA见PROVENANCE.json。

## 可复现工具边界
`integration/run_integration.py`是历史执行脚本的脱敏副本，含路径占位符，不可原样运行或据此覆盖原项目。若需独立重现，另行在新临时目录配置已安装技能路径并复核安全边界；本轮未运行它。两个fixture的`run_tests.py`/`percent.py`/`test_percent.py`可在各自目录用可信Python `python -I -B run_tests.py`执行；故障fixture预期退出1。此包不是新的模型驱动E2E。

## 提交范围
只提交这个证据目录，不修改产品源。基于feat/standard-v1.2.8-migration的独立证据分支；不合并主分支、不打标签、不发布。Owner验收、权利/许可证及正式发布决策均不由材料提交代替。

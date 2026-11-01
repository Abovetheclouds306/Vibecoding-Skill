# SECURITY — 安全模型与边界

本文件描述 vibecoding 技能（`vibecoding/`、`tools/install_skill.py`）**声称**保护什么、**不**保护什么。

## 1. 信任根

- 唯一信任根是技能自带的 `vibecoding/scripts/vb_trust.py` 中固定的 `PINNED_MANIFEST_SHA256`（Vibecoding Standard v1.2.7 的 `MANIFEST.sha256` 的 SHA-256）。
- `vb_trust.py` 先核对清单文件本身等于该哈希，再逐文件核对哈希、缺失与未登记文件；**不执行、不导入**被校验目录里的任何代码。
- 验证命令：`python vibecoding/scripts/vb_trust.py vibecoding/vendor/vibecoding-standard`（PASS = 退出码 0）。
- 标准副本自带的 `tools/verify_manifest.py` 只是 Standard 的自洽性自检，**不是信任根**：篡改者可以同步改写清单使其通过。

## 2. `--standard` / `VB_STANDARD_HOME`

只改变读取位置，**不改变信任判据**：自定义目录同样必须通过固定清单校验，否则 vb_init 拒绝初始化、vb_gate 不执行其中任何脚本且结构校验记 FAIL。vb_gate 通过校验后也只把已核对的 `check_evidence.py` 字节写入私有临时目录，以 `python -I -B` 运行。

## 3. 调用者信任（不在保护范围内）

- `--python`：vb_gate 用它运行结构校验。本工具**不校验解释器本身**；恶意解释器可伪造任何结果。指定即视为你信任它。
- `--verify`：运行的是你自己的命令（经 shell）。门禁只记录退出码与输出，不审查命令内容。
- 技能目录本身（`vibecoding/scripts/`、安装器）：被篡改的技能无法自证清白；请从可信来源获取并核对。

## 4. 威胁模型之外

- **同一用户身份的本地攻击者**：能以你的身份运行代码的进程可以直接改写技能、解释器或项目，不在威胁模型内。
- **临时目录权限**：私有目录由 `tempfile.mkdtemp` 创建。在 Windows 上，未包含 gh-118486 修复的 Python（3.12.4 之前的 3.12、3.11.10 之前的 3.11、3.10.15 之前的 3.10 等）不会给该目录设置限制性 ACL，目录继承 `%TEMP%` 的 ACL；而 `%TEMP%` 可能向其他主体授予修改权限（例如沙箱用户组 `CodexSandboxUsers`）。此时这些主体可能在执行窗口内改写私有副本。请使用已修复的 Python，并检查 `%TEMP%` 的 ACL。
- **TOCTOU / 竞态**：vb_gate 一次读入并核对脚本字节、执行私有副本，消除了“校验标准目录 → 执行标准目录”之间的替换窗口；但私有副本写入到被执行之间仍存在对能写该目录的主体的竞态（见上条）。安装器在源预检与复制之间、以及目标复检时都会核对，但不防同时写入的并发进程。
- **`__pycache__/`**：vb_trust 容忍 `__pycache__/` 内的文件（Python 自身会生成），`__pycache__` 之外的 `.pyc/.pyo` 记为未登记（FAIL）。vb_gate 从不在标准目录导入或执行文件，因此不受影响；但 **vb_trust PASS 不代表可以在该目录原地安全运行标准自带的脚本**。
- **原子性**：安装器与 vb_init 单文件“临时文件 + 替换”写入，**不提供跨文件原子性**；中断后可能残留部分文件（会列出），恢复方式见 `vibecoding/README.md`。

## 5. 报告漏洞

请勿在公开 issue 中披露细节。通过仓库托管平台的私密漏洞报告功能（如 GitHub “Report a vulnerability”）或联系仓库所有者私下报告，附复现步骤、影响版本与平台。所有者确认后再协调披露。
#!/usr/bin/env python3
"""vb_init.py — Vibecoding Skill 受保护初始化（PbC：默认 dry-run，--apply 才落盘）。

约束（与 SKILL.md 铁律一致）：
1. 从不编辑 CLAUDE.md；从不改写 AGENTS.md 标记块之外的内容。
2. 重复执行必须幂等：第二次全部 unchanged，不新增/不改动任何文件。
3. 写入 tracked 文件前若工作区脏，需 --allow-dirty。
4. 标准副本校验不过则拒绝初始化（退出码 1），不写任何文件。
5. 写盘前做可预见检查（目标类型冲突、路径不得越出项目目录）；任何检查不过即拒绝，且尚未写任何文件。
6. 所有写盘经 WriteJournal 登记：**先登记恢复记录再写入**；单条写入先写同目录临时文件，
   再 `os.replace` 原子替换（同卷语义），因此单条写入失败不会留下半截目标文件。
   可控异常按逆序回滚本次写入（只回滚本进程创建/修改、且当前内容仍等于本进程写入值的文件；
   不删除用户原有文件），失败返回非零退出码并打印诊断；无法还原时输出 `ResidualRisk`
   与受影响路径及实际残留状态，且**不再宣称"已全部回滚"**。
7. 每次实际写入前重新核对目标真实位置：越出项目目录、或预检后该路径真实位置发生变化
   （被替换为符号链接 / Junction / 其他重解析点），一律拒绝继续初始化并非零退出。
   回滚、以及单条写入失败后的就地补偿（还原 / 撤销新建）同样受此约束，
   不跟随被替换的路径去删改项目外数据。
   **边界**：这是把 TOCTOU 窗口压到最小，**不是消除**——预检与写入之间仍存在极短窗口，
   `SIGKILL` / 断电 / 文件系统自身非原子行为无法由脚本保证，因此不做跨文件原子提交。

退出码：0 = 成功/无需变更（含 `--update-block` 已按授权更新块）；
        1 = 拒绝或出错（含已完成回滚、或部分回滚仍有残留的失败）；
        2 = 仍需人工决定，且**本次零写入**：标记块/副本是可证明由工具生成的陈旧内容（含 MIXED_STATE）
            而未获 `--update-block` 授权；或存在冲突：config 无法解析/身份不可识别，或 AGENTS.md 标记块 /
            `.vibecoding/AGENTS.block.md` 被用户修改或来源无法证明（USER_MODIFIED / USER_MODIFIED_OR_UNKNOWN）。
            `--update-block` 只授权升级可证明由工具生成的陈旧受管块，**从不**覆盖用户修改或来源不明的内容。

「接入缺失」语义（F-2）：本脚本只使用**已安装技能自带的 vendor 副本**作为规范真值源，
从不把整份规范复制进项目。因此它同时要求：vendor 实际存在、可读、且与签收版本校验一致；
任一不满足即拒绝初始化并说明缺什么。**不宣称"未安装技能也能使用完整规范"。**
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vb_trust  # noqa: E402  R4-N7：固定哈希的可信校验器（技能自带，不执行被校验目录里的脚本）
from datetime import datetime

SKILL_VERSION = "0.1.0"
STANDARD_VERSION = vb_trust.STANDARD_VERSION            # "1.2.8"
STANDARD_SIGNOFF = vb_trust.STANDARD_SIGNOFF            # 工程候选 2e010b0
STANDARD_RELEASE = vb_trust.STANDARD_RELEASE            # 私有正式发布 d9abf27 / v1.2.8
STANDARD_ZIP_SHA = vb_trust.STANDARD_ZIP_SHA

# 旧版识别表（D-6）：只读，仅用于识别升级来源并输出 LEGACY_DETECTED；
# 运行时信任只来自 vb_trust 的固定值，本表中的任何值都**不被信任**。
LEGACY_IDENTITIES = {
    "1.2.7": {
        "standard_signoff_commit": "ce5b361cf13ae373094abe67eb9ce7a6e22ecb8f",
        "standard_release_commit": "fd9750f3e6c4c2105cf253d5f7d6494f0f373fdf",
        "standard_vendor_zip_sha256": "0ce2a06cf506904cca4e0597240d43f5e869ee9845d7b508bc83a9fd2745dd38",
    },
}
# config.json 中参与幂等比较的稳定字段（initialized_at 保留原值）
STABLE_FIELDS = ("skill_version", "standard_version", "standard_signoff_commit",
                 "standard_release_commit", "standard_vendor_zip_sha256", "standard_vendor_path",
                 "standard_trust")

BEGIN = "<!-- vibecoding:begin"
END = "<!-- vibecoding:end -->"

BLOCK = """<!-- vibecoding:begin skill={sv} standard={std} -->
## 工程纪律（Vibecoding v{std}）

本项目遵循 Vibecoding Standard v{std}。以下为不可省略的最低动作，细节见 `.vibecoding/` 与所用的 Agent Skill `vibecoding`。

- **唯一规则真值源**：{std_claim}规则改动只能回到标准仓库发版，不得就地修改。
  - **规范位置**：以 `.vibecoding/config.json` 的 `standard_vendor_path` 字段为准；该目录须含 `AI_PROJECT_STANDARD.md` 与 `MANIFEST.sha256`。
  - **本次初始化解算**：`{vendor_path}`（{vendor_condition}）。
  - **路径不可读时**：说明技能已卸载或项目已移动。此时**不得假装规范已加载**，也不得引用未读到的条款；须重新安装技能后执行 `vb_init.py --project . --apply` 重定位。
- **开工前**：读 `.vibecoding/config.json` 与 `.vibecoding/HANDOFF.md`；确认分支、HEAD 与工作区状态。
- **验证纪律**：结论必须附命令与**实际退出码**。`0=PASS / 1=FAIL / 2=UNKNOWN`；`2` 既不得当通过，也不得当"跳过"。
- **禁止假 PASS**：未运行写 `NOT_RUN`；为了让门禁变绿而放宽测试断言属禁止行为。
- **证据**：一任务一份 `.vibecoding/evidence/<TASK>.md`，含命令、退出码、证据路径、复查条件。
- **交接**：会话中断前更新 `.vibecoding/HANDOFF.md`；新会话先读它再动手。
- **不改他人改动**：不 `reset` / `checkout --` / `clean` / 强推；发现无关改动保留并报告。
<!-- vibecoding:end -->
"""

HANDOFF_TEMPLATE = """<!-- generated-by: vb_handoff v{sv} -->
# {task} 交接

Updated: {ts}
Task source: 见项目自身任务系统（本文件不复制任务状态）
Workspace: {workspace}
Baseline: {baseline}

## 已完成
{summary}

## 验证
{verify}

## 未完成与阻塞
{blocked}

## 已发生的外部效果
{effects}

## 工作区卫生
{hygiene}

## 恢复步骤
1. `git status --porcelain` 确认未提交改动归属。
2. 读 `.vibecoding/evidence/` 下与本任务相关的证据，核对结论与退出码。
3. 按"未完成与阻塞"逐项继续，不重跑已有副作用的步骤。

## 下一步
{next}
"""

EVIDENCE_TEMPLATE = """<!-- generated-by: vb_gate v{sv} -->
# {task} 验证记录

Task: {task}
Time: {ts}
Baseline: {baseline}
Environment: {env}

| 验收 ID | 命令 / 步骤 | 退出码 | 结论 | 证据路径 | 限制 |
| --- | --- | --- | --- | --- | --- |
| AC-001 | <待执行> | NOT_RUN | NOT_RUN | N/A | 由 vb_gate.py 首次运行时生成 |

结论：NOT_RUN
反向遗漏审查：待人工填写（本任务范围、确认的遗漏与处置）
审查：待人工填写（审查者、版本、结论）
Artifacts: N/A
Recheck Conditions: 代码、依赖或测试变更后需重跑
Cleanup / Recovery: N/A
Release Status: 未涉及
"""


def run(args: list[str], cwd: str | None = None, timeout: int = 120) -> tuple[int, str, str]:
    try:
        p = subprocess.run(args, cwd=cwd, capture_output=True, timeout=timeout, shell=False)
        return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")
    except FileNotFoundError:
        return 127, "", "command not found: %s" % args[0]
    except subprocess.TimeoutExpired:
        return 124, "", "timeout: %s" % " ".join(args)


def git(project: str, *args: str) -> tuple[int, str]:
    rc, out, err = run(["git", *args], cwd=project)
    return rc, (out if rc == 0 else err).strip()


def git_state(project: str) -> dict:
    rc, top = git(project, "rev-parse", "--show-toplevel")
    if rc != 0:
        return {"is_repo": False, "root": None, "head": None, "branch": None, "dirty": None, "porcelain": ""}
    _, head = git(project, "rev-parse", "HEAD")
    _, branch = git(project, "rev-parse", "--abbrev-ref", "HEAD")
    _, status = git(project, "status", "--porcelain")
    return {
        "is_repo": True,
        "root": top,
        "head": head,
        "branch": branch,
        "dirty": bool(status),
        "porcelain": status,
    }


def detect_eol(path: str) -> bytes:
    """返回该文件应使用的换行序列：以文件自身为准，避免混行尾。"""
    try:
        data = _read_raw(path)
    except OSError:
        return b"\n"
    crlf = data.count(b"\r\n")
    lf = data.count(b"\n") - crlf
    return b"\r\n" if crlf > lf else b"\n"


def _write_raw(path: str, data: bytes) -> None:
    """唯一内容写盘出口（单测可替换以注入可控异常）。"""
    with open(path, "wb") as fh:
        fh.write(data)


def _read_raw(path: str) -> bytes:
    with open(path, "rb") as fh:
        return fh.read()


def _replace(src: str, dst: str) -> None:
    """原子替换的提交点（单测可替换以注入「提交阶段失败」）。"""
    os.replace(src, dst)


def _atomic_write(path: str, data: bytes) -> None:
    """同目录临时文件 + 原子替换。

    目标文件在成功替换之前**始终未被打开**，因此单条写入失败不会产生半截目标文件
    （这是 R2-N1 的根因修复）。临时文件与目标同目录 ⇒ 同卷 ⇒ Windows 上 `os.replace`
    为原子替换。不承诺断电 / 强杀下的持久性（已在模块 docstring 声明边界）。
    """
    directory = os.path.dirname(os.path.abspath(path)) or "."
    fd, tmp = tempfile.mkstemp(prefix=".vb-w-", suffix=".tmp", dir=directory)
    os.close(fd)
    committed = False
    try:
        _write_raw(tmp, data)
        try:                       # 尽力刷盘；失败不影响"单条写入不产生半截目标"这一性质
            with open(tmp, "rb+") as fh:
                os.fsync(fh.fileno())
        except OSError:
            pass
        _replace(tmp, path)
        committed = True
    finally:
        if not committed:
            try:
                os.remove(tmp)
            except OSError:
                pass


FILE_ATTRIBUTE_REPARSE_POINT = 0x400


def _is_reparse_point(path: str) -> bool:
    """符号链接 / Junction / 其他重解析点。"""
    try:
        if os.path.islink(path):
            return True
    except OSError:
        pass
    isj = getattr(os.path, "isjunction", None)
    if isj is not None:
        try:
            if isj(path):
                return True
        except OSError:
            pass
    try:
        st = os.lstat(path)
    except OSError:
        return False
    return bool(getattr(st, "st_file_attributes", 0) & FILE_ATTRIBUTE_REPARSE_POINT)


def _inside(path_real: str, root_real: str) -> bool:
    # R4-N9：根为盘符根（如 C:\\）或 / 时已以分隔符结尾，不能再拼一个
    prefix = root_real if root_real.endswith(os.sep) else root_real + os.sep
    return path_real == root_real or path_real.startswith(prefix)


def _describe(path: str) -> str:
    """实际残留状态（让 ResidualRisk 报告落在字节数而不是形容词上）。"""
    try:
        if not os.path.exists(path):
            return "不存在"
        if os.path.isdir(path):
            return "目录（未改动）"
        data = _read_raw(path)
        return "%d 字节 sha256=%s" % (len(data), hashlib.sha256(data).hexdigest()[:16])
    except OSError as exc:
        return "不可读(%s)" % exc


class BoundaryError(RuntimeError):
    """目标真实位置越出项目边界，或预检后真实位置被改变（疑似符号链接 / Junction 替换）。"""


class WriteJournal:
    """记录本次运行的文件写入，异常时按逆序回滚。

    契约（R2-N1 / R2-N2 修复后）：
    - **先登记后写**：写入前先把条目（含原始字节）落入 `entries`，所以"写了一半"的文件
      也在回滚范围内，不会被漏掉。
    - **单条原子**：内容先写同目录临时文件，再 `os.replace`；失败时目标文件未被改动。
    - **归属判据**：只回滚"当前内容仍等于本进程写入值"的文件；内容已被他人改动则跳过并报告，
      绝不覆盖他人改动。
    - **边界复核**：每次写入 / 删除 / 回滚 / 单条失败后的补偿还原前重新核对真实位置；
      越界或已被替换则拒绝，不跟随被替换的路径去动项目外数据。
    - **残留如实报告**：无法还原时记入 `residuals`，上层据此禁止打印"已全部回滚"。
    - **不承诺**：SIGKILL / 断电 / 文件系统自身非原子行为下的绝对原子性。
    """

    def __init__(self, root: str | None = None, baseline: dict[str, str] | None = None) -> None:
        self.entries: list[dict] = []
        self.created_dirs: list[str] = []
        self.residuals: list[dict] = []
        self.step = "初始化"
        self.root_abs = os.path.abspath(root) if root else None
        self.root_real = os.path.realpath(root) if root else None
        self.baseline = {os.path.abspath(k): v for k, v in (baseline or {}).items()}

    # ---------------------------------------------------------- 边界守卫
    def guard(self, path: str) -> None:
        """写入 / 删除前的实时边界复核（R2-N2）。不通过即抛 BoundaryError。"""
        if not self.root_abs:
            return
        abs_p = os.path.abspath(path)
        real_p = os.path.realpath(abs_p)
        if not _inside(real_p, self.root_real):
            raise BoundaryError(
                "目标越出项目边界（真实位置 %s 不在 %s 内）" % (real_p, self.root_real))
        prev = self.baseline.get(abs_p)
        if prev is not None and prev != real_p:
            raise BoundaryError(
                "预检后目标真实位置发生变化（预检 %s → 现在 %s），疑似被替换" % (prev, real_p))
        rel = os.path.relpath(abs_p, self.root_abs)
        if rel.startswith(".."):
            raise BoundaryError("目标不在项目目录内: %s" % abs_p)
        cur = self.root_abs
        for part in rel.split(os.sep)[:-1]:
            cur = os.path.join(cur, part)
            if not os.path.exists(cur):
                continue
            # R4-N2：父目录（含本次新建的目录）真实位置与登记不符 ⇒ 被替换（含指向项目内的 Junction）
            bprev = self.baseline.get(os.path.abspath(cur))
            if bprev is not None and os.path.realpath(cur) != bprev:
                raise BoundaryError(
                    "父路径 %s 真实位置已变化（%s → %s），疑似被替换" % (cur, bprev, os.path.realpath(cur)))
            if _is_reparse_point(cur):
                sub_real = os.path.realpath(cur)
                if not _inside(sub_real, self.root_real):
                    raise BoundaryError(
                        "父路径 %s 是重解析点且指向项目外（%s）" % (cur, sub_real))

    # ---------------------------------------------------------- 目录
    def mkdir(self, path: str) -> None:
        """递归创建目录，并记录本进程新建的层级（用于回滚时清理）。"""
        self.guard(path)
        if os.path.isdir(path):
            return
        missing = []
        cur = os.path.abspath(path)
        while not os.path.isdir(cur):
            missing.append(cur)
            parent = os.path.dirname(cur)
            if parent == cur:
                break
            cur = parent
        os.makedirs(path, exist_ok=True)
        self.created_dirs.extend(missing)
        # R4-N2：新建目录登记真实位置，之后被换成 Junction/链接（即使指向项目内）也能被 guard 识别
        for d in missing:
            self.baseline.setdefault(os.path.abspath(d), os.path.realpath(d))

    # ---------------------------------------------------------- 写入
    def write(self, path: str, data: bytes, step: str = "") -> None:
        self.guard(path)
        existed = os.path.exists(path)
        original = None
        if existed:
            try:
                original = _read_raw(path)
            except OSError as exc:
                raise OSError(
                    "无法读取目标文件，拒绝在缺少恢复记录的情况下写入: %s (%s)" % (path, exc))
        entry = {"path": path, "existed": existed, "original": original,
                 "written": data, "step": step or self.step, "state": "pending"}
        self.entries.append(entry)      # 先登记意图：此后任何失败都在回滚范围内（R2-N1）
        try:
            _atomic_write(path, data)
            entry["state"] = "written"
        except BaseException as exc:
            self._compensate(entry, exc)
            raise

    def _compensate(self, entry: dict, exc: BaseException) -> None:
        """单条写入失败后就地收敛：能还原就还原，不能就如实登记残留。"""
        path = entry["path"]
        # R4-N8/R5-N3：先核对边界再读取；边界不通过时不经被替换的路径读取或描述，也不宣称"本次未改动"
        try:
            self.guard(path)
        except BoundaryError as bexc:
            entry["state"] = "residual"
            entry["redirected"] = True   # R7-N1：写入实际落点未知，回滚时原路径收敛也不能证明已还原
            self.residuals.append({
                "path": path,
                "reason": "写入失败后自动还原前边界校验未通过，已停止还原；路径已被重定向/替换，"
                          "本进程写入是否已提交未知：%s（原始失败 %s: %s）" % (bexc, type(exc).__name__, exc),
                "actual": "未检查（路径已被重定向/替换，不跟随读取）",
            })
            return
        try:
            now = _read_raw(path) if os.path.exists(path) else None
        except OSError:
            now = "<unreadable>"
        if now == entry["original"]:
            entry["state"] = "aborted"          # 目标未被改动（原子写失败时的常态）
            return
        # R3-N1：补偿本身也是"改动目标"，写回 / 删除之前必须重新核对边界。
        # 写入失败到补偿执行之间，该路径的父级可能在某一刻被换成指向项目外的
        # Junction / 符号链接；若跟随过去作还原，就会把项目外的同名用户数据
        # 覆盖成项目内原内容、或直接删掉。此处做不到消除 TOCTOU（guard 与随后的
        # 写盘之间仍有极短窗口），只是让"补偿"与"首次写入"受同一套边界约束，
        # 并把无法还原的情况落到 ResidualRisk 上而不是静默放过。
        # （补偿阶段的边界复核已前移到读取之前，见上）
        # R4-N2：归属判据——只有当前内容仍是本进程写入值时才还原/删除；否则可能是他人内容，保留并如实报告
        if now != entry["written"]:
            entry["state"] = "residual"
            self.residuals.append({
                "path": path,
                "reason": "写入失败后当前内容既不是写入前原值也不是本进程写入值（可能被其他进程改动），"
                          "未还原、未删除（原始失败 %s: %s）" % (type(exc).__name__, exc),
                "actual": _describe(path),
            })
            return
        try:
            if entry["existed"]:
                _atomic_write(path, entry["original"])
                entry["state"] = "restored_after_failure"
            else:
                os.remove(path)
                entry["state"] = "removed_after_failure"
        except OSError as exc2:
            entry["state"] = "residual"
            self.residuals.append({
                "path": path,
                "reason": "写入失败后自动还原也失败：%s（原始失败 %s: %s）"
                          % (exc2, type(exc).__name__, exc),
                "actual": _describe(path),
            })

    # ---------------------------------------------------------- 回滚
    def _resolve_residual(self, e: dict, actions: list) -> None:
        """R5-N3：补偿阶段登记的残留，若回滚时边界已通过且已确认收敛到原值，则撤销该残留，避免过期描述。"""
        if e.get("state") == "residual" and e.get("redirected"):
            # R7-N1：失败时路径曾被重定向，本进程写入可能落在别处；原路径内容收敛不等于真实写入位置已还原
            for r in self.residuals:
                if r["path"] == e["path"]:
                    r["actual"] = ("回滚时原路径已为写入前内容；但失败时路径曾被重定向，"
                                   "本进程写入的实际落点未知（未检查），可能已覆盖项目外文件")
            actions.append("Rechecked %s（原路径已收敛，但写入实际落点未知，残留保留）" % e["path"])
            return
        if e.get("state") == "residual":
            self.residuals = [r for r in self.residuals if r["path"] != e["path"]]
            e["state"] = "resolved_in_rollback"
            actions.append("Reconciled %s（补偿阶段残留已在回滚时复核并收敛）" % e["path"])

    def rollback(self) -> list[str]:
        actions: list[str] = []
        for e in reversed(self.entries):
            path = e["path"]
            try:
                self.guard(path)
            except BoundaryError as exc:
                actions.append("Skipped(out-of-boundary) %s (%s)" % (path, exc))
                if e.get("state") != "residual":   # R4-N2：未回滚的条目必须进残留，禁止宣称"已回滚"
                    self.residuals.append({"path": path, "reason": "回滚前边界校验未通过，未回滚：%s" % exc,
                                           "actual": "未检查（不跟随被替换的路径）"})
                continue
            try:
                cur = _read_raw(path) if os.path.exists(path) else None
            except OSError as exc:          # 读不回就不动它
                actions.append("Skipped(unreadable) %s (%s)" % (path, exc))
                self.residuals.append({"path": path, "reason": "回滚时不可读，未回滚：%s" % exc,
                                       "actual": "不可读"})
                continue
            if cur == e["original"]:
                actions.append("Unchanged %s" % path)      # 本来就没改动（含写入已中止）
                self._resolve_residual(e, actions)
                continue
            if cur != e["written"]:
                actions.append("Skipped(modified-by-others) %s" % path)
                if e.get("state") != "residual":
                    self.residuals.append({"path": path, "reason": "内容已被他人改动，未回滚（不覆盖他人改动）",
                                           "actual": _describe(path)})
                continue
            try:
                if e["existed"]:
                    _atomic_write(path, e["original"])
                    actions.append("Restored %s" % path)
                else:
                    os.remove(path)
                    actions.append("Removed %s" % path)
                self._resolve_residual(e, actions)
            except OSError as exc:
                actions.append("Failed %s (%s)" % (path, exc))
                self.residuals.append({
                    "path": path,
                    "reason": "回滚失败：%s" % exc,
                    "actual": _describe(path),
                })
        for d in reversed(self.created_dirs):
            try:
                self.guard(d)
            except BoundaryError as exc:
                actions.append("Skipped(out-of-boundary) %s (%s)" % (d, exc))
                continue
            try:
                os.rmdir(d)
                actions.append("RemovedDir %s" % d)
            except OSError:
                pass                       # 非空或已不存在：保留
        return actions


def preflight(project: str, plan: dict) -> list[str]:
    """写入前的可预见问题检查；返回问题列表（非空即拒绝执行，且尚未写任何文件）。"""
    problems: list[str] = []
    if not os.path.isdir(project):
        return ["项目目录不存在或不是目录: %s" % project]
    root = os.path.realpath(project)

    def inside(p: str) -> bool:
        return _inside(os.path.realpath(p), root)   # R4-N9：复用根安全判定

    targets = ["AGENTS.md", ".vibecoding", ".vibecoding/config.json",
               ".vibecoding/AGENTS.block.md", ".vibecoding/evidence",
               ".vibecoding/evidence/_template.md", ".vibecoding/HANDOFF.md"]
    for rel in targets:
        p = os.path.join(project, rel)
        if not inside(p):
            problems.append("目标路径越出项目目录（拒绝写入）: %s" % p)

    vb = os.path.join(project, ".vibecoding")
    ev = os.path.join(project, ".vibecoding", "evidence")
    agents = os.path.join(project, "AGENTS.md")
    if plan.get("status") == "conflict":
        problems.append(plan.get("detail") or "AGENTS.md 目标类型冲突")
    if os.path.exists(vb) and not os.path.isdir(vb):
        problems.append(".vibecoding 已存在但不是目录: %s" % vb)
    if os.path.exists(ev) and not os.path.isdir(ev):
        problems.append(".vibecoding/evidence 已存在但不是目录: %s" % ev)
    if plan.get("status") != "created" and os.path.isdir(agents) and plan.get("status") != "conflict":
        problems.append("AGENTS.md 是目录，无法作为文件写入: %s" % agents)
    if not os.access(project, os.W_OK):
        problems.append("项目目录不可写: %s" % project)
    return problems


def find_standard(project: str, explicit: str | None) -> tuple[str | None, str]:
    """定位标准副本目录（以 tools/verify_manifest.py 存在作为“看起来像标准副本”的定位条件，仅用于定位，不代表可信；
    可信与否由 verify_standard → vb_trust 固定清单判定）。返回 (路径, 来源说明)。"""
    here = os.path.dirname(os.path.abspath(__file__))
    candidates: list[tuple[str, str]] = []
    if explicit:
        # 显式指定即唯一来源：路径无效时如实拒绝，不得静默回退到其他副本（P1-CLI 技能缺失如实报告）
        if os.path.isfile(os.path.join(explicit, "tools", "verify_manifest.py")):
            return os.path.abspath(explicit), "--standard 参数"
        return None, "--standard 指定的路径不存在或不是有效标准副本（未回退到其他副本）: %s" % explicit
    env = os.environ.get("VB_STANDARD_HOME")
    if env:
        candidates.append((env, "环境变量 VB_STANDARD_HOME"))
    candidates.append((os.path.normpath(os.path.join(here, "..", "vendor", "vibecoding-standard")), "技能内置 vendor"))
    project_vendor = os.path.join(project, ".vibecoding", "vendor", "vibecoding-standard")
    candidates.append((project_vendor, "项目内 .vibecoding/vendor"))

    for path, source in candidates:
        if path and os.path.isfile(os.path.join(path, "tools", "verify_manifest.py")):
            return os.path.abspath(path), source
    return None, "未找到（检查 --standard / VB_STANDARD_HOME / vendor 目录）"


def verify_vendor_access(standard: str) -> list[str]:
    """校验权威 vendor 的实际路径、文件存在性与可读性（F-2）。

    返回问题列表；非空即视为「接入缺失」——拒绝初始化，而不是写一个指向空路径的注入块。
    """
    problems: list[str] = []
    if not os.path.isdir(standard):
        return ["vendor 路径不是目录: %s" % standard]
    doc = os.path.join(standard, "AI_PROJECT_STANDARD.md")
    if not os.path.isfile(doc):
        problems.append("缺少规范正文 AI_PROJECT_STANDARD.md: %s" % doc)
    else:
        try:
            with open(doc, "rb") as fh:
                head = fh.read(1)
            if not head:
                problems.append("规范正文为空文件: %s" % doc)
        except OSError as exc:
            problems.append("规范正文不可读: %s (%s)" % (doc, exc))
    if not os.path.isfile(os.path.join(standard, "MANIFEST.sha256")):
        problems.append("缺少 MANIFEST.sha256（无法证明与签收版本一致）: %s" % standard)
    if not os.path.isfile(os.path.join(standard, "tools", "verify_manifest.py")):
        problems.append("缺少 tools/verify_manifest.py（无法自校验）: %s" % standard)
    return problems


VENDOR_COND_RELATIVE = "项目内相对路径，随项目整体移动仍有效；技能被卸载则该路径消失"
VENDOR_COND_ABSOLUTE = "项目外绝对路径，与本机技能安装位置绑定；换机器或移动技能后失效，需重新 --apply 重定位"


def vendor_reference(project: str, standard: str) -> dict:
    """把已定位的 vendor 转成「可写进项目文件 + 可被 Agent 解析」的引用（F-2）。

    - 在项目内 → 写项目相对路径（随项目整体移动仍有效）。
    - 在项目外 → 写绝对路径，并如实标注其与本机安装位置绑定、换机器或移动技能后失效。
    **不复制整份规范进项目**（只引用，不产生第二份规则副本）。
    """
    root = os.path.realpath(project)
    real = os.path.realpath(standard)
    if _inside(real, root):
        rel = os.path.relpath(real, root).replace("\\", "/")
        return {
            "path": rel,
            "kind": "project_relative",
            "inside_project": True,
            "condition": VENDOR_COND_RELATIVE,
        }
    return {
        "path": os.path.abspath(standard).replace("\\", "/"),
        "kind": "absolute_external",
        "inside_project": False,
        "condition": VENDOR_COND_ABSOLUTE,
    }


def verify_standard(standard: str, python_exe: str) -> tuple[int, list[str]]:
    """R4-N7：用技能自带、固定哈希的校验器核对；不运行被校验目录自带的 verify_manifest.py。
    python_exe 保留参数位以兼容旧调用，不再用于校验。"""
    rc, lines = vb_trust.verify_pinned(standard)
    return rc, lines[-6:]


STD_CLAIM_TRUSTED = "Vibecoding Standard v{std} 正文，只读，与签收版本逐字节相同。"
STD_CLAIM_SKIPPED = ("Vibecoding Standard v{std} 正文，只读。**本次初始化使用了 --skip-standard-check，"
                     "规范副本未经校验，不得视为签收版本**；去掉该参数重新 --apply 才能确认。")


def split_block(text: str) -> tuple[int, int] | None:
    """返回标记块的 (start, end) 字节偏移（字符索引），无块返回 None。"""
    i = text.find(BEGIN)
    if i < 0:
        return None
    j = text.find(END, i)
    if j < 0:
        return None
    return i, j + len(END)


def normalize(text: str) -> str:
    """Ownership compare normalization: CRLF->LF, per-line rstrip, strip ends.\n\n    Not raw byte equality. Trailing whitespace / newline style / leading-trailing blank\n    lines are indistinguishable from tool output for ownership. BOM / lone CR / in-line\n    whitespace changes are outside this normalization (usually USER_MODIFIED; safe refuse).\n    """
    return "\n".join(line.rstrip() for line in text.replace("\r\n", "\n").split("\n")).strip()


def plan_agents(project: str, desired_block: str) -> dict:
    path = os.path.join(project, "AGENTS.md")
    if not os.path.exists(path):
        return {"file": "AGENTS.md", "status": "created", "detail": "不存在，将创建并写入标记块", "path": path}
    if os.path.isdir(path):
        return {"file": "AGENTS.md", "status": "conflict",
                "detail": "AGENTS.md 是目录，无法作为文件读写: %s" % path, "path": path}
    raw = _read_raw(path)
    text = raw.decode("utf-8", "replace")
    span = split_block(text)
    if span is None:
        return {"file": "AGENTS.md", "status": "appended", "detail": "存在且无标记块，将在文件末尾追加（原有内容不动）", "path": path}
    existing = text[span[0]:span[1]]
    if normalize(existing) == normalize(desired_block):
        return {"file": "AGENTS.md", "status": "unchanged", "detail": "标记块已存在且一致（幂等）", "path": path}
    return {"file": "AGENTS.md", "status": "differs", "detail": "标记块存在但内容不同，需 --update-block 才更新", "path": path}


def apply_agents(plan: dict, desired_block: str, update_block: bool, project: str,
                 journal: WriteJournal) -> str:
    path = plan["path"]
    if plan["status"] in ("unchanged", "differs"):
        if plan["status"] == "differs":
            if not update_block:
                return "skipped(需 --update-block)"
            raw = _read_raw(path)
            text = raw.decode("utf-8", "replace")
            span = split_block(text)
            eol = "\r\n" if detect_eol(path) == b"\r\n" else "\n"
            new = text[:span[0]] + desired_block.replace("\n", eol).rstrip("\r\n") + text[span[1]:]
            journal.write(path, new.encode("utf-8"), step="AGENTS.md 更新标记块")
            return "block_updated"
        return "no_change"

    eol_bytes = detect_eol(path) if os.path.exists(path) else b"\n"
    block_bytes = desired_block.replace("\n", eol_bytes.decode()).rstrip("\r\n").encode("utf-8")

    if plan["status"] == "created":
        journal.write(path, block_bytes + eol_bytes, step="AGENTS.md 创建")
        return "created"

    existing = _read_raw(path)
    payload = bytearray(existing)
    if existing and not existing.endswith(b"\n"):
        payload += eol_bytes
    payload += eol_bytes
    payload += block_bytes
    payload += eol_bytes
    journal.write(path, bytes(payload), step="AGENTS.md 追加标记块")
    return "appended"


def write_if_changed(path: str, content: bytes, journal: WriteJournal | None = None) -> str:
    if os.path.exists(path):
        if _read_raw(path) == content:
            return "unchanged"
        return "differs"
    if journal is not None:
        journal.mkdir(os.path.dirname(path))
        journal.write(path, content, step="写入 %s" % os.path.basename(path))
    else:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        _write_raw(path, content)
    return "created"


HEADER_RE = re.compile(r"<!-- vibecoding:begin skill=(\S+) standard=(\S+) -->")


def _block_std(text: str | None) -> str | None:
    m = HEADER_RE.search(text or "")
    return m.group(2) if m else None


# ---------------------------------------------------------------- 受管块归属判据
# AGENTS.md 标记块与 .vibecoding/AGENTS.block.md 只有在**normalize 后等于**某个可信生成契约的
# 渲染结果时，才被认定为“工具生成”。normalize = CRLF→LF、逐行 rstrip、整体 strip（不是原始逐字节比较）。
# 可信生成契约 = 本文件内冻结的模板文本 × 已发布工具版本 × 已知标准版本 × 冻结的校验声明
# × **仅**由本次工具独立解算得到的规范定位（vendor_reference / 本次传入的 vref）。
# - **从不**采用可编辑的 `.vibecoding/config.json`（含 `standard_vendor_path`）参与可信渲染；
# - **从不**从待验证的标记块 / 副本中提取版本 / 路径再渲染来证明它可信；
# - **从不**以“标记块 == 副本”推断未被修改（两处都可被用户改成相同内容）；
# - 无法证明来源 → USER_MODIFIED（版本可识别）/ USER_MODIFIED_OR_UNKNOWN，rc=2 零写入，--update-block 也不覆盖。
#   项目或技能移动后、旧块路径与本次解算不一致时，保守拒绝并交人工处置（安全方向）。
# 旧版模板只用于只读识别；运行时信任仍只来自 vb_trust 的单一固定清单。
# v1.2.7 工具（skill 0.1.0）生成的块模板，逐字冻结；SHA-256 由测试钉住。
LEGACY_BLOCK_TEMPLATE_V127 = """<!-- vibecoding:begin skill={sv} standard={std} -->
## 工程纪律（Vibecoding v{std}）

本项目遵循 Vibecoding Standard v{std}。以下为不可省略的最低动作，细节见 `.vibecoding/` 与所用的 Agent Skill `vibecoding`。

- **唯一规则真值源**：{std_claim}规则改动只能回到标准仓库发版，不得就地修改。
  - **规范位置**：以 `.vibecoding/config.json` 的 `standard_vendor_path` 字段为准；该目录须含 `AI_PROJECT_STANDARD.md` 与 `MANIFEST.sha256`。
  - **本次初始化解算**：`{vendor_path}`（{vendor_condition}）。
  - **路径不可读时**：说明技能已卸载或项目已移动。此时**不得假装规范已加载**，也不得引用未读到的条款；须重新安装技能后执行 `vb_init.py --project . --apply` 重定位。
- **开工前**：读 `.vibecoding/config.json` 与 `.vibecoding/HANDOFF.md`；确认分支、HEAD 与工作区状态。
- **验证纪律**：结论必须附命令与**实际退出码**。`0=PASS / 1=FAIL / 2=UNKNOWN`；`2` 既不得当通过，也不得当"跳过"。
- **禁止假 PASS**：未运行写 `NOT_RUN`；为了让门禁变绿而放宽测试断言属禁止行为。
- **证据**：一任务一份 `.vibecoding/evidence/<TASK>.md`，含命令、退出码、证据路径、复查条件。
- **交接**：会话中断前更新 `.vibecoding/HANDOFF.md`；新会话先读它再动手。
- **不改他人改动**：不 `reset` / `checkout --` / `clean` / 强推；发现无关改动保留并报告。
<!-- vibecoding:end -->
"""
LEGACY_BLOCK_TEMPLATE_V127_SHA256 = "cc8882721d097a8bd1f1f54a4ed9ce10612a52e0f1703f9c691b7c130f7adf43"
LEGACY_STD_CLAIMS_V127 = (
    "Vibecoding Standard v{std} 正文，只读，与签收版本逐字节相同。",
    ("Vibecoding Standard v{std} 正文，只读。**本次初始化使用了 --skip-standard-check，"
                     "规范副本未经校验，不得视为签收版本**；去掉该参数重新 --apply 才能确认。"),
)
# (标准版本, 模板, 生成过该标准的工具版本, 声明模板)
TRUSTED_GENERATION = (
    ("1.2.7", LEGACY_BLOCK_TEMPLATE_V127, ("0.1.0",), LEGACY_STD_CLAIMS_V127),
    (STANDARD_VERSION, BLOCK, (SKILL_VERSION,), (STD_CLAIM_TRUSTED, STD_CLAIM_SKIPPED)),
)
KNOWN_STANDARD_VERSIONS = tuple(g[0] for g in TRUSTED_GENERATION)
OWNERSHIP_REASON = ("内容不等于任何可信生成契约（冻结模板 × 已发布工具版本 × 已知标准版本 × 本次工具独立解算的规范定位）"
                    "的渲染结果，无法证明由工具生成；--update-block 只升级可证明由工具生成的陈旧受管块，不覆盖用户修改或来源不明的内容；"
                    "可编辑 config.json 不参与归属证明")
MANUAL_GUIDANCE = (
    "本次未写入任何文件（rc=2）；--update-block 不会覆盖上述内容。",
    "对照下方有限差异确认哪些改动需要保留；需保留的内容请移到 AGENTS.md 标记块之外（工具从不改动标记块外的字节）。",
    "然后人工删除 AGENTS.md 中整个 vibecoding 标记块（含 begin / end 两行）和/或 .vibecoding/AGENTS.block.md，再运行 vb_init.py --apply 重新生成。",
    "差异只在本地输出、不上传；现有内容只给行号 / 长度 / SHA-256 前缀，不回显正文（可能含敏感信息）。",
)
DIFF_MAX_LINES = 12


def trusted_renderings(vref: dict) -> dict:
    """normalize(trusted rendering) -> standard version.

    Inputs are frozen constants plus THIS RUN's independently resolved vref only.
    Never reads the block/copy under test, and never reads editable
    config.json.standard_vendor_path (N1 / R16 recheck).
    """
    out: dict = {}
    path, cond = vref["path"], vref["condition"]
    for std, tpl, svs, claims in TRUSTED_GENERATION:
        for sv in svs:
            for claim in claims:
                out.setdefault(normalize(tpl.format(sv=sv, std=std, std_claim=claim.format(std=std),
                                                    vendor_path=path, vendor_condition=cond)), std)
    return out


def classify_managed(text: str, desired_block: str, trusted: dict) -> str:
    """unchanged / TOOL_GENERATED_STALE / USER_MODIFIED / USER_MODIFIED_OR_UNKNOWN（逐文件独立判定）。"""
    n = normalize(text)
    if n == normalize(desired_block):
        return "unchanged"
    if n in trusted:
        return "TOOL_GENERATED_STALE"
    return "USER_MODIFIED" if _block_std(text) in KNOWN_STANDARD_VERSIONS else "USER_MODIFIED_OR_UNKNOWN"


def _clip(s: str, n: int = 80) -> str:
    return s if len(s) <= n else s[:n] + "…"


def limited_diff(expected: str, actual: str, label: str) -> list:
    """有限差异：期望侧（工具模板文本）截断显示；现有侧只给行号 / 长度 / SHA-256 前缀，不回显正文。"""
    import difflib
    e = normalize(expected).split("\n")
    a = normalize(actual).split("\n")
    ops = [o for o in difflib.SequenceMatcher(None, e, a, autojunk=False).get_opcodes() if o[0] != "equal"]
    body = []
    for _tag, i1, i2, j1, j2 in ops:
        for k in range(i1, i2):
            body.append("  - 期望 L%d: %s" % (k + 1, _clip(e[k])))
        for k in range(j1, j2):
            body.append("  + 现有 L%d: <%d 字符, sha256:%s>"
                        % (k + 1, len(a[k]), hashlib.sha256(a[k].encode("utf-8")).hexdigest()[:12]))
    head = ["%s 有限差异：期望侧 %d 行、现有侧 %d 行不同（现有内容不回显正文）"
            % (label, sum(o[2] - o[1] for o in ops), sum(o[4] - o[3] for o in ops))]
    if len(body) > DIFF_MAX_LINES:
        body = body[:DIFF_MAX_LINES] + ["  … 其余 %d 行差异已省略" % (len(body) - DIFF_MAX_LINES)]
    return head + body


def _diff_base(text: str, desired_block: str, vref: dict) -> str:
    """差异基准：被测内容声明的旧标准版本若已知，用该版本的可信渲染（仅用于展示，不参与信任判定）。"""
    std = _block_std(text)
    for s, tpl, svs, claims in TRUSTED_GENERATION:
        if s == std and s != STANDARD_VERSION:
            return tpl.format(sv=svs[0], std=s, std_claim=claims[0].format(std=s),
                              vendor_path=vref["path"], vendor_condition=vref["condition"])
    return desired_block


def config_identity(cfg: dict) -> str | None:
    """返回 "current" / "legacy" / None（不可识别 → 不推断、不覆盖）。"""
    v = cfg.get("standard_version")
    cur = {"standard_signoff_commit": STANDARD_SIGNOFF, "standard_release_commit": STANDARD_RELEASE,
           "standard_vendor_zip_sha256": STANDARD_ZIP_SHA}
    if v == STANDARD_VERSION and all(cfg.get(k) == cur[k] for k in cur):
        return "current"
    leg = LEGACY_IDENTITIES.get(v) if isinstance(v, str) else None
    if leg and all(cfg.get(k) == leg[k] for k in leg):
        return "legacy"
    return None


def _agents_block_text(project: str) -> str | None:
    path = os.path.join(project, "AGENTS.md")
    if not os.path.isfile(path):
        return None
    text = _read_raw(path).decode("utf-8", "replace")
    span = split_block(text)
    return text[span[0]:span[1]] if span else None


def read_markers(project: str) -> dict:
    out: dict = {"config": None, "AGENTS.md": _block_std(_agents_block_text(project)),
                 ".vibecoding/AGENTS.block.md": None}
    cp = os.path.join(project, ".vibecoding", "AGENTS.block.md")
    if os.path.isfile(cp):
        out[".vibecoding/AGENTS.block.md"] = _block_std(_read_raw(cp).decode("utf-8", "replace"))
    cfg = os.path.join(project, ".vibecoding", "config.json")
    if os.path.isfile(cfg):
        try:
            data = json.loads(_read_raw(cfg).decode("utf-8"))
            out["config"] = data.get("standard_version") if isinstance(data, dict) else None
        except (ValueError, OSError):
            out["config"] = None
    return out


def verify_consistent(project: str, desired_block: str) -> list[str]:
    """写后复核：config、副本、AGENTS.md 标记块三处都必须是本版本、且块内容与期望一致。"""
    bad = []
    m = read_markers(project)
    if m["config"] != STANDARD_VERSION:
        bad.append("config.json standard_version=%r" % m["config"])
    cp = os.path.join(project, ".vibecoding", "AGENTS.block.md")
    if not os.path.isfile(cp) or normalize(_read_raw(cp).decode("utf-8", "replace")) != normalize(desired_block):
        bad.append(".vibecoding/AGENTS.block.md 与期望块不一致")
    blk = _agents_block_text(project)
    if blk is None or normalize(blk) != normalize(desired_block):
        bad.append("AGENTS.md 标记块与期望块不一致")
    return bad


def EVIDENCE_TEMPLATE_BYTES() -> bytes:
    return EVIDENCE_TEMPLATE.format(sv=SKILL_VERSION, task="<TASK-ID>", ts="<日期 时间 时区>",
                                    baseline="<commit>", env="<系统 / 运行时>").encode("utf-8")


def build_plan(project: str, agents_plan: dict, desired_block: str, manifest: dict,
               vref: dict | None = None) -> dict:
    """只读地构建完整计划；不写任何文件。"""
    if vref is None:
        _p = manifest["standard_vendor_path"]
        vref = {"path": _p, "condition": VENDOR_COND_ABSOLUTE if (_p.startswith("/") or re.match(r"^[A-Za-z]:/", _p))
                else VENDOR_COND_RELATIVE}
    vb = os.path.join(project, ".vibecoding")
    out: dict = {"conflicts": [], "auth": [], "legacy": None, "config_bytes": None, "copy_diff": []}

    # 1) config.json
    cfg_path = os.path.join(vb, "config.json")
    new_cfg = dict(manifest)
    prev_std = None
    if not os.path.lexists(cfg_path):
        out["config"] = "created"
    elif not os.path.isfile(cfg_path):
        out["config"] = "conflict"
        out["conflicts"].append(".vibecoding/config.json 不是普通文件")
    else:
        try:
            prev = json.loads(_read_raw(cfg_path).decode("utf-8"))
            if not isinstance(prev, dict):
                raise ValueError("不是 JSON 对象")
        except (ValueError, OSError) as exc:
            out["config"] = "conflict"
            out["conflicts"].append(".vibecoding/config.json 无法解析（%s）：来源不明确，不推断、不覆盖" % type(exc).__name__)
        else:
            prev_std = prev.get("standard_version")
            if all(prev.get(k) == manifest.get(k) for k in STABLE_FIELDS):
                out["config"] = "unchanged"
            else:
                ident = config_identity(prev)
                if ident is None:
                    out["config"] = "conflict"
                    out["conflicts"].append(".vibecoding/config.json 记录的标准身份不可识别（standard_version=%r）："
                                            "来源不明确，不推断、不覆盖" % (prev_std,))
                else:
                    out["config"] = "updated"
                    if ident == "legacy":
                        out["legacy"] = prev_std
                    new_cfg["initialized_at"] = prev.get("initialized_at") or manifest["initialized_at"]
    out["config_bytes"] = (json.dumps(new_cfg, ensure_ascii=False, indent=2) + "\n").encode("utf-8")

    # 2) / 3) 受管块归属：AGENTS.md 标记块与副本逐文件独立判定（见“受管块归属判据”）。
    # N1: trusted renderings use this-run vref only; never config.standard_vendor_path.
    trusted = trusted_renderings(vref)
    out["user_modified"] = []
    out["agents_diff"] = []

    def _protect(name: str, path: str, text: str, diff_key: str) -> str:
        cls = classify_managed(text, desired_block, trusted)
        if cls in ("USER_MODIFIED", "USER_MODIFIED_OR_UNKNOWN"):
            out["user_modified"].append({"file": name, "path": path, "classification": cls,
                                         "reason": OWNERSHIP_REASON})
            out["conflicts"].append("%s: %s（%s）：%s" % (cls, name, path, OWNERSHIP_REASON))
            out[diff_key] = limited_diff(_diff_base(text, desired_block, vref), text, name)
        return cls

    agents_text = _agents_block_text(project) if agents_plan["status"] in ("unchanged", "differs") else None
    if agents_plan["status"] == "differs":
        cls = _protect("AGENTS.md 标记块", agents_plan["path"], agents_text, "agents_diff")
        if cls == "TOOL_GENERATED_STALE":
            out["auth"].append("AGENTS.md 标记块与期望不同（工具生成的陈旧内容，standard=%s）" % _block_std(agents_text))
        else:
            out["agents_conflict"] = True

    cp = os.path.join(vb, "AGENTS.block.md")
    if not os.path.lexists(cp):
        out["copy"] = "created"
    elif not os.path.isfile(cp):
        out["copy"] = "conflict"
        out["conflicts"].append(".vibecoding/AGENTS.block.md 不是普通文件")
    else:
        text = _read_raw(cp).decode("utf-8", "replace")
        cls = _protect(".vibecoding/AGENTS.block.md", cp, text, "copy_diff")
        if cls == "unchanged":
            out["copy"] = "unchanged"
        elif cls == "TOOL_GENERATED_STALE":
            out["copy"] = "stale"
            out["auth"].append(".vibecoding/AGENTS.block.md 副本陈旧（工具生成，standard=%s）" % _block_std(text))
        else:
            out["copy"] = "conflict"

    # 4) evidence/_template.md（存在且不同 → 保留，不写）
    ev = os.path.join(vb, "evidence", "_template.md")
    if not os.path.lexists(ev):
        out["evidence"] = "created"
    elif os.path.isfile(ev) and _read_raw(ev) == EVIDENCE_TEMPLATE_BYTES():
        out["evidence"] = "unchanged"
    else:
        out["evidence"] = "differs"

    # 5) HANDOFF.md（仅不存在时创建）
    out["handoff"] = "exists(unchanged)" if os.path.lexists(os.path.join(vb, "HANDOFF.md")) else "created"

    # 6) MIXED_STATE（D-2）：已存在的三处 standard= 标记不一致
    markers = {"config": prev_std, "AGENTS.md": _block_std(agents_text),
               ".vibecoding/AGENTS.block.md": _block_std(_read_raw(cp).decode("utf-8", "replace"))
               if os.path.isfile(cp) else None}
    out["markers"] = markers
    present = {v for v in markers.values() if v is not None}
    out["mixed"] = len(present) > 1
    if out["mixed"] and not out["auth"] and not out["conflicts"]:
        out["auth"].append("MIXED_STATE")
    return out


def print_residuals(residuals: list[dict]) -> bool:
    """打印残留风险；返回是否存在残留（存在时上层禁止宣称"已全部回滚"）。"""
    if not residuals:
        return False
    print("--- 残留风险（ResidualRisk）---")
    for r in residuals:
        print("  ResidualRisk %s" % r["path"])
        print("      原因     : %s" % r["reason"])
        print("      实际残留 : %s" % r["actual"])
    print("  说明: 上述路径未能还原为写入前状态，请人工核对后再使用该项目。")
    return True


def _main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Vibecoding Skill 受保护初始化（默认 dry-run）",
                                 allow_abbrev=False)   # R4-N6：禁止前缀缩写（--jso/--app 等）
    ap.add_argument("--project", default=".", help="目标项目目录（默认当前目录）")
    ap.add_argument("--standard", help="标准副本目录（只改变读取位置；仍须通过技能自带 vb_trust 的固定 v1.2.8 清单校验，否则拒绝）")
    ap.add_argument("--apply", action="store_true", help="实际落盘；缺省为 dry-run")
    ap.add_argument("--allow-dirty", action="store_true", help="工作区脏时仍允许改 tracked 文件")
    ap.add_argument("--update-block", action="store_true", help="授权升级可证明由工具生成的陈旧受管块（AGENTS.md 标记块 / .vibecoding/AGENTS.block.md / config.json）；用户修改或来源无法证明的内容（USER_MODIFIED / USER_MODIFIED_OR_UNKNOWN）一律 rc=2 零写入，不会被覆盖")
    ap.add_argument("--skip-standard-check", action="store_true", help="跳过标准副本完整性校验（不推荐）")
    ap.add_argument("--python", default=sys.executable, help="保留参数（兼容旧调用）；R4-N7 起初始化不再执行标准目录中的任何工具")
    ap.add_argument("--json", action="store_true", help="以 JSON 输出结果")
    args = ap.parse_args(argv)

    project = os.path.abspath(args.project)
    if not os.path.isdir(project):
        print("ERROR: 项目目录不存在: %s" % project)
        return 1

    result: dict = {"project": project, "mode": "apply" if args.apply else "dry-run", "steps": [], "rc": 0}

    standard, source = find_standard(project, args.standard)
    if not standard:
        print("REFUSED: 未找到标准副本（接入缺失）。%s" % source)
        print("  接入缺失的含义：本技能不带第二份规范副本，规范正文必须来自已安装技能的 vendor。")
        print("  处置：重新安装技能（或安装到项目内 <项目>/.claude/skills/vibecoding），再执行一次 --apply。")
        return 1
    result["standard"] = {"path": standard, "source": source}

    access = verify_vendor_access(standard)
    if access:
        print("REFUSED: 规范接入缺失（未写入任何文件）。")
        for p in access:
            print("  - " + p)
        print("  不写指向空路径的注入块：那会让后续会话误以为规范已加载。")
        return 1
    vref = vendor_reference(project, standard)
    result["standard"]["vendor_ref"] = vref

    if not args.skip_standard_check:
        rc, tail = verify_standard(standard, args.python)
        result["standard"]["verify_rc"] = rc
        result["standard"]["verify_tail"] = tail
        if rc != 0:
            print("REFUSED: 标准副本完整性校验未通过（退出码 %d），未写入任何文件。" % rc)
            for line in tail:
                print("  " + line)
            print("  信任边界：只接受与固定的 v%s 签收清单（SHA-256 %s…）逐文件一致的副本；"
                  "--standard / VB_STANDARD_HOME 只改变读取位置，不改变信任判据。"
                  % (STANDARD_VERSION, vb_trust.PINNED_MANIFEST_SHA256[:16]))
            legacy = vb_trust.legacy_version(standard)
            if legacy:
                print("  LEGACY_DETECTED: 该副本是旧版 v%s 的清单（只读识别，不被信任）；请安装携带 v%s 的技能。"
                      % (legacy, STANDARD_VERSION))
            return 1
        result["standard"]["trust"] = vb_trust.TRUST_PINNED
    else:
        result["standard"]["verify_rc"] = None
        result["standard"]["verify_tail"] = ["SKIPPED：--skip-standard-check，标准副本未经校验，不是签收版本声明"]
        result["standard"]["trust"] = vb_trust.TRUST_SKIPPED
    std_claim = (STD_CLAIM_SKIPPED if args.skip_standard_check else STD_CLAIM_TRUSTED).format(std=STANDARD_VERSION)

    state = git_state(project)
    result["git"] = {k: state[k] for k in ("is_repo", "root", "head", "branch", "dirty")}

    desired_block = BLOCK.format(sv=SKILL_VERSION, std=STANDARD_VERSION, std_claim=std_claim,
                                 vendor_path=vref["path"], vendor_condition=vref["condition"])
    plan = plan_agents(project, desired_block)

    # 规范位置：项目内用相对路径（随项目移动有效），项目外用绝对路径（并已标注失效条件）。
    # 不再使用 os.path.relpath 生成"越出项目"的 ../../ 相对路径（R2 的 F-2 事实之一）。
    manifest = {
        "skill_version": SKILL_VERSION,
        "standard_version": STANDARD_VERSION,
        "standard_signoff_commit": STANDARD_SIGNOFF,
        "standard_release_commit": STANDARD_RELEASE,
        "standard_vendor_zip_sha256": STANDARD_ZIP_SHA,
        "standard_vendor_path": vref["path"],
        "standard_trust": result["standard"]["trust"],
        "initialized_at": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z"),
    }

    # S-SKILL-01（R15 A/B/C；D-1/D-2/D-3）：任何写入之前先构建**完整**计划。
    # 需授权（陈旧块/副本）而未给 --update-block、或存在来源不明确的冲突 → rc=2，零写入；
    # dry-run 与 apply 使用同一份计划与同一写入集合。
    full = build_plan(project, plan, desired_block, manifest, vref)
    blocked = bool(full["conflicts"]) or (bool(full["auth"]) and not args.update_block)
    agents_write = (not blocked) and (plan["status"] in ("created", "appended")
                                      or (plan["status"] == "differs" and args.update_block))
    writes = {
        "AGENTS.md": agents_write,
        ".vibecoding/config.json": (not blocked) and full["config"] in ("created", "updated"),
        ".vibecoding/AGENTS.block.md": (not blocked) and full["copy"] in ("created", "stale"),
        ".vibecoding/evidence/_template.md": (not blocked) and full["evidence"] == "created",
        ".vibecoding/HANDOFF.md": (not blocked) and full["handoff"] == "created",
    }
    result["plan"] = {
        "markers": full["markers"],
        "mixed_state": full["mixed"],
        "legacy_detected": full["legacy"],
        "needs_authorization": full["auth"],
        "conflicts": full["conflicts"],
        "write_set": sorted(k for k, v in writes.items() if v),
        "copy_diff": full["copy_diff"],
        "agents_diff": full.get("agents_diff", []),
        "user_modified": full["user_modified"],
        "manual_guidance": list(MANUAL_GUIDANCE) if full["user_modified"] else [],
    }

    touch_tracked = agents_write and (plan["status"] in ("appended", "differs")
                                      or (plan["status"] == "created" and state["is_repo"]))
    if args.apply and not blocked and state["dirty"] and touch_tracked and not args.allow_dirty:
        print("REFUSED: 工作区有未提交改动，且本次会修改 AGENTS.md。确认无冲突后加 --allow-dirty。")
        print(state["porcelain"] or "(status 为空但 dirty 判定为真)")
        return 1

    labels = {
        ".vibecoding/config.json": full["config"],
        ".vibecoding/AGENTS.block.md": "updated" if full["copy"] == "stale" else full["copy"],
        ".vibecoding/evidence/_template.md": full["evidence"],
        ".vibecoding/HANDOFF.md": full["handoff"],
    }

    def _step(name: str, status: str) -> dict:
        return {"file": name, "status": status, "write": writes[name]}

    if not args.apply:
        # 被阻断的 dry-run 不显示 would_*：与 apply 相同，本次不会写任何文件。
        if blocked:
            plan["action"] = "no_change" if plan["status"] == "unchanged" else "blocked(not_written:%s)" % plan["status"]
        else:
            plan["action"] = "would_" + plan["status"]
        plan["write"] = writes["AGENTS.md"]
        result["steps"].append(plan)
        for name, lab in labels.items():
            if lab in ("unchanged", "exists(unchanged)") and (blocked or name == ".vibecoding/HANDOFF.md"):
                result["steps"].append(_step(name, lab))
            elif blocked:
                result["steps"].append(_step(name, "blocked(not_written:%s)" % lab))
            else:
                result["steps"].append(_step(name, "would_" + lab))
    elif blocked:
        # 零写入：不建目录、不开 journal（D-1）
        why = "冲突" if full["conflicts"] else "需 --update-block"
        plan["action"] = ("skipped(需 --update-block)" if plan["status"] == "differs" and not full["conflicts"]
                          else ("skipped(%s)" % why if plan["status"] != "unchanged" else "no_change"))
        plan["write"] = False
        result["steps"].append(plan)
        for name, lab in labels.items():
            status = lab if lab in ("unchanged", "exists(unchanged)") else "not_written(%s)" % why
            result["steps"].append(_step(name, status))
    else:
        # 预检前的真实位置基线：写入时若与它不一致 → 目标在预检后被替换（R2-N2）
        baseline: dict[str, str] = {}
        for _rel in ("", ".vibecoding", ".vibecoding/evidence", "AGENTS.md"):
            _p = os.path.join(project, _rel) if _rel else project
            if os.path.exists(_p):
                baseline[os.path.abspath(_p)] = os.path.realpath(_p)
        journal = WriteJournal(root=project, baseline=baseline)
        problems = preflight(project, plan)
        if problems:
            print("REFUSED: 写入前检查未通过（未写入任何文件）。")
            for p in problems:
                print("  - " + p)
            return 1
        done = dict(labels)
        cfg_path = os.path.join(project, ".vibecoding", "config.json")
        try:
            if any(writes.values()):
                journal.step = "创建 .vibecoding/ 目录"
                journal.mkdir(os.path.join(project, ".vibecoding"))
                journal.mkdir(os.path.join(project, ".vibecoding", "evidence"))
            if writes[".vibecoding/config.json"]:
                journal.step = ".vibecoding/config.json"
                journal.write(cfg_path, full["config_bytes"], step=".vibecoding/config.json %s"
                              % ("更新" if full["config"] == "updated" else "创建"))
            if writes[".vibecoding/AGENTS.block.md"]:
                journal.step = ".vibecoding/AGENTS.block.md"
                journal.write(os.path.join(project, ".vibecoding", "AGENTS.block.md"),
                              desired_block.encode("utf-8"), step=".vibecoding/AGENTS.block.md %s"
                              % ("更新" if full["copy"] == "stale" else "创建"))
            if writes[".vibecoding/evidence/_template.md"]:
                journal.step = ".vibecoding/evidence/_template.md"
                journal.write(os.path.join(project, ".vibecoding", "evidence", "_template.md"),
                              EVIDENCE_TEMPLATE_BYTES(), step="写入 _template.md")
            if writes[".vibecoding/HANDOFF.md"]:
                journal.step = ".vibecoding/HANDOFF.md"
                ws = "%s @ %s" % (state["branch"], state["head"][:12]) if state["is_repo"] else project
                hbase = state["head"] if state["is_repo"] else "无版本基线"
                journal.write(os.path.join(project, ".vibecoding", "HANDOFF.md"), HANDOFF_TEMPLATE.format(
                    sv=SKILL_VERSION,
                    task="<TASK-ID>",
                    ts=datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z"),
                    workspace=ws,
                    baseline=hbase,
                    summary="（待填写）",
                    verify="（待填写）",
                    blocked="（待填写）",
                    effects="无",
                    hygiene="无",
                    next="（待填写）",
                ).encode("utf-8"), step=".vibecoding/HANDOFF.md 创建")

            # 最后才动用户的 tracked 文件，缩短"已改用户文件"的时间窗
            journal.step = "AGENTS.md"
            plan["action"] = apply_agents(plan, desired_block, args.update_block, project, journal)

            # 写后复核（D-3）：config / 副本 / AGENTS.md 三处必须一致，否则抛错 → 回滚 → rc=1，绝不报告成功
            journal.step = "写后复核三处一致性"
            bad = verify_consistent(project, desired_block)
            if bad:
                raise RuntimeError("MIXED_STATE：写后复核不一致（%s；标记 %s）"
                                   % ("; ".join(bad), read_markers(project)))
        except BoundaryError as exc:      # R2-N2：越界或目标被替换，停止初始化
            actions = journal.rollback()
            print("REFUSED: 检测到越界写入风险，已停止初始化（未继续其余步骤）。")
            print("  原因     : %s" % exc)
            print("  说明     : 预检与写入之间目标真实位置发生变化，可能是符号链接 / Junction / 其他重解析点。")
            print("             这不能证明操作恶意，但无法保证写入落在项目内，故拒绝继续。")
            print("--- 回滚动作 ---")
            for a in actions:
                print("  " + a)
            print_residuals(journal.residuals)
            print("== 结论: REFUSED（边界风险，退出码 1）==")
            return 1
        except Exception as exc:  # 可控异常：回滚本次写入，不删除用户原有文件
            actions = journal.rollback()
            has_residual = bool(journal.residuals)
            # 有残留时不得用完成式措辞，只能说"已尝试"（R2-N1 第 5 条）
            print("ERROR: 初始化失败，%s。" % (
                "已尝试按逆序回滚本次写入（存在未还原项）" if has_residual
                else "已按逆序回滚本次写入"))
            print("  失败步骤 : %s" % journal.step)
            print("  异常类型 : %s" % type(exc).__name__)
            print("  异常信息 : %s" % exc)
            print("--- 回滚动作 ---")
            for a in actions:
                print("  " + a)
            if print_residuals(journal.residuals):
                print("== 结论: FAILED（回滚不完整，存在残留，退出码 1）==")
            else:
                print("== 结论: FAILED（已回滚，退出码 1）==")
            return 1
        except KeyboardInterrupt:  # 用户中断：同样回滚本次写入，绝不报告完成
            actions = journal.rollback()
            print("INTERRUPTED: 初始化被中断，未完成；%s。" % (
                "已尝试按逆序回滚本次写入（存在未还原项）" if journal.residuals else "已按逆序回滚本次写入"))
            print("  中断步骤 : %s" % journal.step)
            print("--- 回滚动作 ---")
            for a in actions:
                print("  " + a)
            if print_residuals(journal.residuals):
                print("== 结论: INTERRUPTED（未完成，回滚不完整，存在残留，退出码 130）==")
            else:
                print("== 结论: INTERRUPTED（未完成，已回滚，退出码 130）==")
            return 130

        _WRITE_PHASE["done"] = True   # R9-F5：写入已提交；此后的中断不得声称“未写入文件”
        plan["write"] = writes["AGENTS.md"]
        result["steps"].append(plan)
        for name, lab in done.items():
            result["steps"].append(_step(name, lab))

    claude_md = os.path.join(project, "CLAUDE.md")
    if os.path.exists(claude_md):
        result["manual_required"] = [
            "检测到 CLAUDE.md：本脚本不会编辑它。",
            "Claude Code 默认仅在工作目录及其上方都没有 CLAUDE.md 类文件时才读 AGENTS.md。",
            "解法一：Project instructions 设为 claude-md-and-agents-md。",
            "解法二：在 CLAUDE.md 首行加入 @AGENTS.md。",
        ]
    # 退出码反映**操作完成后**的真实状态（F-5 / S-SKILL-01）：
    # - 存在冲突（来源不明确 / 副本被用户修改）→ 2，零写入
    # - 需授权（陈旧块/副本、MIXED_STATE）且未给 --update-block → 2，零写入
    # - 其余：已按计划写入且写后复核一致 → 0（异常与复核失败在上面已回滚并返回 1）
    action = plan.get("action", "")
    needs_decision = blocked
    result["rc"] = 2 if needs_decision else 0
    result["needs_decision"] = needs_decision
    result["conflict"] = bool(full["conflicts"])
    result["block_updated"] = (action == "block_updated")

    if args.json:
        result["status"] = "needs_decision" if result["rc"] == 2 else "ok"
        _JSON_RESULT.append(result)
    else:
        print("== Vibecoding 初始化（%s）==" % result["mode"])
        print("项目      : %s" % project)
        print("标准来源  : %s" % source)
        print("标准副本  : %s" % standard)
        print("规范定位  : %s（%s）" % (vref["path"], vref["condition"]))
        if result["standard"]["verify_rc"] is None:
            print("标准校验  : SKIPPED（未验证；不是签收版本声明）")
        else:
            print("标准校验  : rc=%s %s" % (result["standard"]["verify_rc"],
                  "PASS（固定 v%s 清单）" % STANDARD_VERSION if result["standard"]["verify_rc"] == 0 else "见下"))
        for line in result["standard"]["verify_tail"]:
            print("            " + line)
        print("Git       : %s" % ("repo=%s branch=%s head=%s dirty=%s" % (state["is_repo"], state["branch"], (state["head"] or "")[:12], state["dirty"]) if state["is_repo"] else "非 Git 仓库"))
        pl = result.get("plan") or {}
        if pl.get("legacy_detected"):
            print("LEGACY_DETECTED: 项目记录为旧版 v%s（只读识别；旧版身份不被信任，需 --update-block 授权升级到 v%s）"
                  % (pl["legacy_detected"], STANDARD_VERSION))
        if pl.get("mixed_state"):
            print("MIXED_STATE: 三处标准版本标记不一致 %s" % json.dumps(pl.get("markers"), ensure_ascii=False))
        for c in pl.get("conflicts") or []:
            print("CONFLICT: " + c)
        for line in (pl.get("agents_diff") or []) + (pl.get("copy_diff") or []):
            print("    " + line)
        if pl.get("manual_guidance"):
            print("--- USER_MODIFIED 人工处置 ---")
            for n_, g in enumerate(pl["manual_guidance"], 1):
                print("  %d. %s" % (n_, g))
        for a in pl.get("needs_authorization") or []:
            print("需授权: " + a)
        print("--- 步骤 ---")
        for step in result["steps"]:
            print("  %-34s %-18s %s" % (step.get("file"), step.get("status"), step.get("action", "")))
        if result.get("manual_required"):
            print("--- 需人工处理 ---")
            for line in result["manual_required"]:
                print("  " + line)
        if result["rc"] == 2 and result.get("conflict") and pl.get("user_modified"):
            verdict = "NEED_DECISION / CONFLICT（%s：受管块被用户修改或来源无法证明；未写入任何文件，退出码 2）" % (
                "/".join(sorted({u["classification"] for u in pl["user_modified"]})))
        elif result["rc"] == 2 and result.get("conflict"):
            verdict = "NEED_DECISION / CONFLICT（来源不明确或副本被修改；未写入任何文件，退出码 2）"
        elif result["rc"] == 2:
            verdict = "NEED_DECISION（%s，未获 --update-block 授权；未写入任何文件）" % (
                "MIXED_STATE" if (result.get("plan") or {}).get("mixed_state") else "标记块/副本 differs")
        elif result["block_updated"]:
            verdict = "OK（标记块已更新）"
        else:
            verdict = "OK"
        print("== 结论: %s ==" % verdict)
    return result["rc"]

# ------------------------------------------------ --json 输出契约（P1-CLI-1）
# 成功路径：输出 result（含 status=ok|needs_decision、rc、steps …）。
# 任何非成功路径（拒绝 / 失败 / 参数错误 / 未预期异常）：也只输出一个 JSON 对象，
#   {"status": "refused"|"failed"|"usage_error", "rc": <与进程退出码相同>, "error": <首条说明>,
#    "messages": [<原散文逐行>], "mode", "project", "steps": [], "needs_decision": false, "block_updated": false}
# stdout 上不再出现 JSON 以外的散文。
_JSON_RESULT: list = []
_WRITE_PHASE = {"done": False}


def _interrupt_message() -> str:
    if _WRITE_PHASE["done"]:
        return "INTERRUPTED: 初始化被中断（中断发生在写入阶段完成之后：本次计划的文件已写入、未回滚，仅输出未完成；可重跑 --apply 核对，幂等）。退出码 130"
    return "INTERRUPTED: 初始化被中断，未完成（中断发生在写入阶段之外，未写入文件）。退出码 130"


def main(argv: list[str]) -> int:
    _WRITE_PHASE["done"] = False
    if "--json" not in argv:
        try:
            return _main(argv)
        except KeyboardInterrupt:  # 写入阶段之外的中断：预检/校验时（未写入）或写入完成后（已写入）
            print(_interrupt_message())
            return 130
    del _JSON_RESULT[:]
    buf = io.StringIO()
    usage_error = False
    help_shown = False
    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            rc = _main(argv)
    except SystemExit as exc:  # argparse：--help（code 0）或用法错误
        if exc.code in (0, None):
            rc = 0
            help_shown = True
        else:
            rc = exc.code if isinstance(exc.code, int) else 2
            usage_error = True
    except KeyboardInterrupt:
        buf.write(_interrupt_message() + "\n")
        rc = 130
    except Exception as exc:  # noqa: BLE001 — JSON 模式下也要给出契约内的失败结果
        buf.write("ERROR: 未预期异常 %s: %s\n" % (type(exc).__name__, exc))
        rc = 1
    lines = [l.rstrip() for l in buf.getvalue().splitlines() if l.strip()]
    if help_shown:
        # --json --help：明确标记为帮助输出，不是一次初始化结果
        payload = {"status": "ok", "kind": "help", "help": True, "rc": 0, "error": "", "messages": lines,
                   "mode": "help", "project": None, "steps": [], "needs_decision": False, "block_updated": False}
    elif _JSON_RESULT and _JSON_RESULT[-1].get("rc") == rc and not usage_error:
        payload = _JSON_RESULT[-1]
        if lines:
            payload["messages"] = lines
    else:
        first = lines[0] if lines else ""
        status = ("usage_error" if usage_error else "refused" if first.startswith("REFUSED")
                  else "interrupted" if first.startswith("INTERRUPTED") else "failed")
        # R4-N6：mode/project 用与 _main 相同的解析规则推导（支持 --project=X，不认缩写）
        mp = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
        mp.add_argument("--project")
        mp.add_argument("--apply", action="store_true")
        try:
            with contextlib.redirect_stderr(io.StringIO()):
                known, _ = mp.parse_known_args(argv)
        except SystemExit:
            known = None
        proj = os.path.abspath(known.project) if known is not None and known.project else None
        payload = {"status": status, "rc": rc, "error": first, "messages": lines,
                   "mode": "apply" if known is not None and known.apply else "dry-run", "project": proj,
                   "steps": [], "needs_decision": False, "block_updated": False}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

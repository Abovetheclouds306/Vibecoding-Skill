#!/usr/bin/env python3
"""vb_trust.py — 规范副本的可信校验器（R4-N7，Owner 裁定）。

信任根是**本文件里固定的哈希**，不是被校验目录自带的 `tools/verify_manifest.py`：
1. 被校验目录的 `MANIFEST.sha256` 的 SHA-256 必须等于 PINNED_MANIFEST_SHA256（Vibecoding Standard v1.2.9
   / tag `v1.2.9`，MIT，YunAbove）；
2. 清单登记的每个文件 SHA-256 必须与清单一致，且不得缺失；
3. 除 `MANIFEST.sha256` 与 `__pycache__/` 目录外，不得有未登记文件；`__pycache__` 之外的 `.pyc/.pyo`
   一律算未登记（R10-N1：无源 .pyc 可被同目录脚本导入）。`__pycache__` 不被信任也不被使用：
   vb_gate 只执行从已校验字节复制到私有临时目录的 check_evidence.py，并以 `-I -B` 运行。
全部满足才返回 0；否则返回 1。本模块只读，不执行被校验目录里的任何代码。

自定义 `--standard` / `VB_STANDARD_HOME` 只改变**从哪里读**，不改变**信任什么**：
内容与固定清单不一致的副本一律判 FAIL，不会被当作签收版本。
"""
from __future__ import annotations

import hashlib
import os
import re
import sys

STANDARD_VERSION = "1.2.9"
# 工程候选签收（S-SKILL-01）；v1.2.8 私有正式发布见 LEGACY；现行为 v1.2.9（MIT）
STANDARD_SIGNOFF = "2e010b04059172b651c191bf1dbaab279c8d78be"
STANDARD_RELEASE = "b1ece9f5743d4330524da7b813f6852b7cbc75ad"
STANDARD_TAG = "v1.2.9"
STANDARD_ZIP_SHA = "ddaba6788a79f61abf570e886b515fd318d67ace87d3cce73f08204818471946"
# vendor/vibecoding-standard/MANIFEST.sha256（git archive b1ece9f）的 SHA-256
PINNED_MANIFEST_SHA256 = "46035ee2c0d0063564a3215ea411f80d51ce0d18088a6cda879f525f9e9ec19e"
PINNED_FILE_COUNT = 38          # 清单登记文件数（另加 MANIFEST.sha256 本身 = 39）
# 旧版识别表：只读，仅用于输出 LEGACY_DETECTED；运行时只信任上面的固定值。
LEGACY_MANIFEST_SHA256 = {
    "1.2.7": "68d8a834eaab9b0106bfa2dbc651bf9f67daee848f28262230140ac958ff6cd0",
    "1.2.8": "28303d4c5548bf3d464c5e70c04e607da7e58645c0e3904f9c4c52202e88304c",
}
TRUST_PINNED = "pinned-signed-off-v%s" % STANDARD_VERSION
TRUST_SKIPPED = "unverified-skipped"

_LINE = re.compile(r"^([0-9a-f]{64}) [ *](.+)$")
_SKIP_DIRS = {"__pycache__"}


def _sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_pinned(standard: str) -> tuple[int, list[str]]:
    """返回 (rc, 说明行)。rc 0 = 与固定 STANDARD_VERSION 清单逐文件一致；1 = 不一致或无法证明。"""
    lines: list[str] = []
    mpath = os.path.join(standard, "MANIFEST.sha256")
    try:
        mh = _sha256(mpath)
        with open(mpath, "rb") as fh:
            raw = fh.read().decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return 1, ["!! 无法读取 MANIFEST.sha256: %s" % exc, "== 可信校验: FAIL（无法证明为签收版本）=="]
    if mh != PINNED_MANIFEST_SHA256:
        return 1, ["!! MANIFEST.sha256 的 SHA-256 与固定值不符（期望 %s… 实际 %s…）"
                   % (PINNED_MANIFEST_SHA256[:16], mh[:16]),
                   "   该目录不是 Vibecoding Standard v%s 签收版本（自定义/被改动的副本不被信任）" % STANDARD_VERSION,
                   "== 可信校验: FAIL（清单未固定匹配）=="]
    entries: dict[str, str] = {}
    for n, line in enumerate(raw.splitlines(), 1):
        if not line.strip():
            continue
        m = _LINE.match(line.strip())
        if not m:
            return 1, ["!! 清单第 %d 行格式无效" % n, "== 可信校验: FAIL =="]
        name = m.group(2).strip()
        parts = name.split("/")
        if os.path.isabs(name) or ".." in parts or "\\" in name:
            return 1, ["!! 清单含非法路径: %s" % name, "== 可信校验: FAIL =="]
        entries[name] = m.group(1)
    bad, missing = [], []
    for name, expect in sorted(entries.items()):
        p = os.path.join(standard, *name.split("/"))
        if not os.path.isfile(p):
            missing.append(name)
        elif _sha256(p) != expect:
            bad.append(name)
    extra = []
    for dp, dns, fns in os.walk(standard):
        dns[:] = [d for d in dns if d not in _SKIP_DIRS]
        for f in fns:
            rel = os.path.relpath(os.path.join(dp, f), standard).replace(os.sep, "/")
            if rel == "MANIFEST.sha256":
                continue
            if rel not in entries:
                extra.append(rel)
    for name in bad:
        lines.append("!! 哈希不符: %s" % name)
    for name in missing:
        lines.append("!! 缺失: %s" % name)
    for name in extra:
        lines.append("!! 未登记文件: %s" % name)
    ok = not bad and not missing and not extra and len(entries) == PINNED_FILE_COUNT
    lines.append("== 可信校验: %s（固定清单 v%s；通过 %d / 失败 %d / 缺失 %d / 未登记 %d）=="
                 % ("PASS" if ok else "FAIL", STANDARD_VERSION, len(entries) - len(bad) - len(missing),
                    len(bad), len(missing), len(extra)))
    return (0 if ok else 1), lines


def legacy_version(standard: str) -> str | None:
    """只读识别：若目录的 MANIFEST.sha256 等于旧版识别表中的值，返回旧版本号；否则 None。
    返回值只用于提示（LEGACY_DETECTED），不改变 verify_pinned 的判定。"""
    try:
        mh = _sha256(os.path.join(standard, "MANIFEST.sha256"))
    except OSError:
        return None
    for ver, sha in LEGACY_MANIFEST_SHA256.items():
        if mh == sha:
            return ver
    return None


def read_verified(standard: str, rel: str) -> bytes | None:
    """R10-N2：一次读入并核对单个文件字节（清单须等于固定值、该文件哈希须等于清单登记值）。
    返回已核对的字节；调用方只使用这份内存中的字节，不再回读目录（消除校验与执行之间的替换窗口）。"""
    try:
        with open(os.path.join(standard, "MANIFEST.sha256"), "rb") as fh:
            mraw = fh.read()
        if hashlib.sha256(mraw).hexdigest() != PINNED_MANIFEST_SHA256:
            return None
        expect = None
        for line in mraw.decode("utf-8").splitlines():
            m = _LINE.match(line.strip())
            if m and m.group(2).strip() == rel:
                expect = m.group(1)
        if expect is None:
            return None
        with open(os.path.join(standard, *rel.split("/")), "rb") as fh:
            data = fh.read()
    except (OSError, UnicodeDecodeError):
        return None
    return data if hashlib.sha256(data).hexdigest() == expect else None


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "vendor", "vibecoding-standard")
    rc, out = verify_pinned(os.path.abspath(target))
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    print("\n".join(out))
    sys.exit(rc)
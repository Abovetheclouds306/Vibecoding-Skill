# -*- coding: utf-8 -*-
"""S-SKILL-01：v1.2.7 → v1.2.8 迁移与 R15 A/B/C 修复的回归测试。

覆盖：旧版识别、未授权零写入（rc2）、授权后三处一致、MIXED_STATE、副本被修改冲突、
不可识别 config 冲突、dry-run 写入集合 == apply 实际改动、写入 / 复核失败回滚、幂等、
用户文件保护、Git 与非 Git 升级、旧 vendor 拒绝（LEGACY_DETECTED）、无 --upgrade 参数。
"""
from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import tarfile
import unittest
from unittest import mock

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from test_vb_init import Base, snapshot, run_main, vb_init, block_of, _rm_tree  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, ".."))
OLD = "1.2.7"
NEW = vb_init.STANDARD_VERSION
def rd(p, **kw):
    with open(p, encoding="utf-8", **kw) as fh:
        return fh.read()


def wr(p, text, mode="w", **kw):
    with open(p, mode, encoding="utf-8", **kw) as fh:
        fh.write(text)


def rb(p):
    with open(p, "rb") as fh:
        return fh.read()


def legacy_block(proj, skipped=False):
    """渲染可证明的 v1.2.7 工具块：用冻结模板 × 旧版身份 × 本次独立解算的 vendor_path。

    禁止对全文做 NEW→OLD 字符串替换：工作树/技能路径若含版本号（如 …-v1.2.8-migration），
    会把规范绝对路径改坏，归属判定变成 USER_MODIFIED 假红。
    """
    home = vb_init.find_standard(proj, None)[0]
    vref = vb_init.vendor_reference(proj, home)
    sv = vb_init.TRUSTED_GENERATION[0][2][0]
    claim = vb_init.LEGACY_STD_CLAIMS_V127[1 if skipped else 0].format(std=OLD)
    return vb_init.LEGACY_BLOCK_TEMPLATE_V127.format(
        sv=sv, std=OLD, std_claim=claim,
        vendor_path=vref["path"], vendor_condition=vref["condition"])


def _with_file_eol(text_lf: str, path: str) -> str:
    """模板为 LF；按目标文件既有 EOL 写出，避免 CRLF 文件上字符串替换静默失败。"""
    eol = vb_init.detect_eol(path).decode("ascii") if os.path.isfile(path) else "\n"
    return text_lf.replace("\n", "\r\n") if eol == "\r\n" else text_lf


def install_legacy_blocks(proj, agents=True, copy=True, skipped=False):
    leg = legacy_block(proj, skipped=skipped)
    if agents:
        p = os.path.join(proj, "AGENTS.md")
        t = rd(p, newline="")
        span = vb_init.split_block(t)
        if span is None:
            raise AssertionError("install_legacy_blocks: AGENTS.md 无 vibecoding 标记块")
        s, e = span
        wr(p, t[:s] + _with_file_eol(leg, p) + t[e:], newline="")
    if copy:
        p = os.path.join(proj, ".vibecoding", "AGENTS.block.md")
        wr(p, _with_file_eol(leg, p), newline="")
    markers = vb_init.read_markers(proj)
    if agents and markers.get("AGENTS.md") != OLD:
        raise AssertionError("install_legacy_blocks: AGENTS.md 未变为 legacy: %r" % markers)
    if copy and markers.get(".vibecoding/AGENTS.block.md") != OLD:
        raise AssertionError("install_legacy_blocks: 副本未变为 legacy: %r" % markers)
    home = vb_init.find_standard(proj, None)[0]
    trusted = vb_init.trusted_renderings(vb_init.vendor_reference(proj, home))
    if agents:
        cls = vb_init.classify_managed(block_of(proj), "unused-desired", trusted)
        if cls != "TOOL_GENERATED_STALE":
            raise AssertionError("install_legacy_blocks: AGENTS 块非 TOOL_GENERATED_STALE: %s" % cls)
    if copy:
        cls = vb_init.classify_managed(
            rd(os.path.join(proj, ".vibecoding", "AGENTS.block.md"), newline=""),
            "unused-desired", trusted)
        if cls != "TOOL_GENERATED_STALE":
            raise AssertionError("install_legacy_blocks: 副本非 TOOL_GENERATED_STALE: %s" % cls)


GITC = ["-c", "user.name=vbtest", "-c", "user.email=vbtest@example.invalid", "-c", "commit.gpgsign=false"]


class Mig(Base):
    def init_json(self, *extra):
        rc, out = self.init("--json", *extra)
        return rc, json.loads(out)

    def make_legacy(self, agents=True, copy=True, config=True, user_text=True):
        """先用新版初始化，再把选定的三处改写成 v1.2.7 工具产物（路径保持本次解算值）。"""
        if user_text:
            self.write("AGENTS.md", "# 用户规则\n\n保留这一段。\n")
        rc, out = self.init("--apply")
        self.assertEqual(rc, 0, out)
        install_legacy_blocks(self.proj, agents=agents, copy=copy, skipped=False)
        if config:
            p = os.path.join(self.proj, ".vibecoding", "config.json")
            cfg = json.loads(rd(p))
            cfg.update(vb_init.LEGACY_IDENTITIES[OLD], standard_version=OLD,
                       standard_trust="pinned-signed-off-v" + OLD, initialized_at="2026-10-01 00:00:00 +0800")
            wr(p, json.dumps(cfg, ensure_ascii=False, indent=2) + "\n")

    def assert_consistent(self):
        self.assertEqual(vb_init.verify_consistent(self.proj, self.desired()), [])
        m = vb_init.read_markers(self.proj)
        self.assertEqual(set(m.values()), {NEW}, m)

    def desired(self):
        """期望块：在独立空目录用同一工具全新初始化得到（不读被测项目，避免自证）。"""
        import tempfile
        d = tempfile.mkdtemp(prefix="vbfresh-")
        try:
            rc, out = run_main(["--project", d, "--apply"])
            assert rc == 0, out
            return rd(os.path.join(d, ".vibecoding", "AGENTS.block.md"))
        finally:
            _rm_tree(d)


class TestLegacyUpgrade(Mig):
    def test_stale_without_update_block_rc2_zero_writes(self):
        """R15-A/B：陈旧（旧版）且未给 --update-block → rc2，三处一个字节都不改。"""
        self.make_legacy()
        before = snapshot(self.proj)
        rc, out = self.init()                      # dry-run
        self.assertEqual(rc, 2, out)
        rc, out = self.init("--apply")
        self.assertEqual(rc, 2, out)
        self.assertIn("LEGACY_DETECTED", out)
        self.assertIn("未写入任何文件", out)
        self.assertEqual(snapshot(self.proj), before, "未授权时不得写任何文件")
        self.assertEqual(set(vb_init.read_markers(self.proj).values()), {OLD})

    def test_upgrade_non_git_consistent_idempotent_user_files_kept(self):
        """非 Git：授权升级后三处一致；用户文件保留；再次运行零改动（幂等）。"""
        self.make_legacy()
        ho = os.path.join(self.proj, ".vibecoding", "HANDOFF.md")
        wr(ho, "\n用户交接笔记\n", "a")
        ev = os.path.join(self.proj, ".vibecoding", "evidence", "_template.md")
        wr(ev, "\n用户自定义证据模板\n", "a")
        ho_b, ev_b = rb(ho), rb(ev)
        rc, out = self.init("--apply", "--update-block")
        self.assertEqual(rc, 0, out)
        self.assert_consistent()
        self.assertEqual(rb(ho), ho_b, "HANDOFF.md 不得被改写")
        self.assertEqual(rb(ev), ev_b, "用户修改过的证据模板不得被覆盖")
        self.assertIn("保留这一段。", self.read("AGENTS.md").decode("utf-8"))
        cfg = json.loads(self.read(".vibecoding/config.json"))
        self.assertEqual(cfg["standard_signoff_commit"], vb_init.STANDARD_SIGNOFF)
        self.assertEqual(cfg["standard_release_commit"], vb_init.STANDARD_RELEASE)
        self.assertEqual(cfg["initialized_at"], "2026-10-01 00:00:00 +0800", "initialized_at 保留原值")
        snap = snapshot(self.proj)
        for extra in ((), ("--update-block",)):
            rc, out = self.init("--apply", *extra)
            self.assertEqual(rc, 0, out)
            self.assertEqual(snapshot(self.proj), snap, "重复运行必须零改动")

    def test_upgrade_git_repo(self):
        """Git：干净工作区内授权升级 → rc0，三处一致，仅改动计划内文件。"""
        self.make_legacy()
        self.assertEqual(self.git("init", "-q").returncode, 0)
        self.git("add", "-A")
        self.assertEqual(self.git(*GITC, "commit", "-q", "-m", "legacy").returncode, 0)
        rc, out = self.init("--apply")
        self.assertEqual(rc, 2, out)
        self.assertEqual(self.git("status", "--porcelain").stdout.strip(), b"", "未授权不得产生改动")
        rc, out = self.init("--apply", "--update-block")
        self.assertEqual(rc, 0, out)
        self.assert_consistent()
        changed = sorted(l[3:] for l in self.git("status", "--porcelain").stdout.decode().splitlines())
        self.assertEqual(changed, [".vibecoding/AGENTS.block.md", ".vibecoding/config.json", "AGENTS.md"])

    def test_dry_run_write_set_equals_apply(self):
        """D-3：dry-run 声明的写入集合 == apply 实际改动的文件集合。"""
        self.make_legacy()
        rc, j = self.init_json("--update-block")
        self.assertEqual(rc, 0)
        declared = set(j["plan"]["write_set"])
        flagged = {s["file"] for s in j["steps"] if s.get("write")}
        self.assertEqual(declared, flagged)
        before = snapshot(self.proj)
        rc, out = self.init("--apply", "--update-block")
        self.assertEqual(rc, 0, out)
        after = snapshot(self.proj)
        actual = {k for k in set(before) | set(after) if before.get(k) != after.get(k)}
        self.assertEqual(actual, declared)

    def test_dry_run_blocked_write_set_empty(self):
        self.make_legacy()
        rc, j = self.init_json()
        self.assertEqual(rc, 2)
        self.assertEqual(j["plan"]["write_set"], [])
        self.assertEqual(j["plan"]["legacy_detected"], OLD)


class TestPartialStates(Mig):
    def test_copy_stale_only_needs_authorization(self):
        """R15-C：只有副本陈旧（AGENTS.md 与 config 已是新版）→ 未授权 rc2 零写入；授权后一致。"""
        self.make_legacy(agents=False, config=False)
        before = snapshot(self.proj)
        rc, out = self.init("--apply")
        self.assertEqual(rc, 2, out)
        self.assertEqual(snapshot(self.proj), before)
        rc, out = self.init("--apply", "--update-block")
        self.assertEqual(rc, 0, out)
        self.assert_consistent()

    def test_mixed_state_config_only(self):
        """D-2：仅 config 为旧版 → MIXED_STATE，rc2 零写入；授权后一致。"""
        self.make_legacy(agents=False, copy=False)
        before = snapshot(self.proj)
        rc, out = self.init("--apply")
        self.assertEqual(rc, 2, out)
        self.assertIn("MIXED_STATE", out)
        self.assertEqual(snapshot(self.proj), before)
        rc, out = self.init("--apply", "--update-block")
        self.assertEqual(rc, 0, out)
        self.assert_consistent()

    def test_mixed_state_reported_from_r15_end_state(self):
        """R15 旧缺陷终态（AGENTS 1.2.8 / 副本 1.2.7 / config 1.2.8）→ 不得报告成功。"""
        self.make_legacy(agents=False, config=False)
        rc, out = self.init()
        self.assertEqual(rc, 2, out)
        self.assertNotIn("== 结论: OK", out)

    def test_user_modified_copy_is_conflict_even_with_update_block(self):
        """D-5：副本被用户修改（不等于任何渲染结果）→ CONFLICT rc2，--update-block 也不覆盖。"""
        self.make_legacy()
        p = os.path.join(self.proj, ".vibecoding", "AGENTS.block.md")
        wr(p, "\n用户加的一行\n", "a")
        before = snapshot(self.proj)
        for extra in ((), ("--update-block",), ("--update-block", "--allow-dirty")):
            rc, out = self.init("--apply", *extra)
            self.assertEqual(rc, 2, out)
            self.assertIn("CONFLICT", out)
            # 契约变更：有限差异只给行号 / 长度 / 哈希，不回显用户内容（可能含敏感信息）
            self.assertIn("有限差异", out, "应展示差异")
            self.assertIn("sha256:", out)
            self.assertNotIn("用户加的一行", out)
            self.assertEqual(snapshot(self.proj), before)

    def test_user_modified_agents_block_is_conflict_even_with_update_block(self):
        """§4：AGENTS.md 标记块被用户改动（不等于副本或任何渲染结果）→ CONFLICT rc2，--update-block 也不覆盖。"""
        self.make_legacy()
        p = os.path.join(self.proj, "AGENTS.md")
        t = rd(p)
        i = t.index(vb_init.END)
        wr(p, t[:i] + "用户在块内加的一行\n" + t[i:])
        before = snapshot(self.proj)
        for extra in ((), ("--update-block",), ("--update-block", "--allow-dirty")):
            rc, out = self.init("--apply", *extra)
            self.assertEqual(rc, 2, out)
            self.assertIn("CONFLICT", out)
            self.assertIn("有限差异", out, "应展示差异")
            self.assertIn("sha256:", out)
            self.assertNotIn("用户在块内加的一行", out)
            self.assertEqual(snapshot(self.proj), before)
        rc, out = self.init("--update-block", "--json")
        j = __import__("json").loads(out)
        self.assertEqual(j["plan"]["write_set"], [])

    def test_unparseable_config_is_conflict(self):
        self.make_legacy()
        self.write(".vibecoding/config.json", "{not json")
        before = snapshot(self.proj)
        rc, out = self.init("--apply", "--update-block")
        self.assertEqual(rc, 2, out)
        self.assertIn("CONFLICT", out)
        self.assertEqual(snapshot(self.proj), before)

    def test_unknown_identity_config_is_conflict(self):
        self.make_legacy()
        p = os.path.join(self.proj, ".vibecoding", "config.json")
        cfg = json.loads(rd(p))
        cfg["standard_version"] = "9.9.9"
        wr(p, json.dumps(cfg))
        before = snapshot(self.proj)
        rc, out = self.init("--apply", "--update-block")
        self.assertEqual(rc, 2, out)
        self.assertIn("不可识别", out)
        self.assertEqual(snapshot(self.proj), before)

    def test_legacy_identity_with_wrong_commit_is_conflict(self):
        """版本号写 1.2.7 但提交 SHA 不符 → 不推断，冲突。"""
        self.make_legacy()
        p = os.path.join(self.proj, ".vibecoding", "config.json")
        cfg = json.loads(rd(p))
        cfg["standard_signoff_commit"] = "0" * 40
        wr(p, json.dumps(cfg))
        rc, out = self.init("--apply", "--update-block")
        self.assertEqual(rc, 2, out)


class TestRollback(Mig):
    def test_verify_failure_rolls_back(self):
        """写后复核不一致 → MIXED_STATE 异常 → WriteJournal 回滚到写前字节，rc1。"""
        self.make_legacy()
        before = snapshot(self.proj)
        with mock.patch.object(vb_init, "verify_consistent", lambda *a: ["injected"]):
            rc, out = self.init("--apply", "--update-block")
        self.assertEqual(rc, 1, out)
        self.assertIn("MIXED_STATE", out)
        self.assertIn("FAILED（已回滚", out)
        self.assertEqual(snapshot(self.proj), before)

    def test_write_failure_mid_plan_rolls_back(self):
        """写副本时失败（config 已写）→ 全部回滚，rc1，不留混合状态。"""
        self.make_legacy()
        before = snapshot(self.proj)
        real = vb_init._replace

        def rep(src, dst):
            if os.path.basename(dst) == "AGENTS.block.md":
                raise OSError(28, "injected")
            return real(src, dst)
        with mock.patch.object(vb_init, "_replace", rep):
            rc, out = self.init("--apply", "--update-block")
        self.assertEqual(rc, 1, out)
        self.assertEqual(snapshot(self.proj), before)
        self.assertEqual(set(vb_init.read_markers(self.proj).values()), {OLD})


class TestTrustAndCli(Mig):
    def test_trust_pins_only_new_version(self):
        import importlib.util
        sp = importlib.util.spec_from_file_location("vbt", os.path.join(REPO, "vibecoding", "scripts", "vb_trust.py"))
        m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
        self.assertEqual(m.STANDARD_VERSION, NEW)
        self.assertNotIn(m.PINNED_MANIFEST_SHA256, m.LEGACY_MANIFEST_SHA256.values())
        rc, _ = m.verify_pinned(os.path.join(REPO, "vibecoding", "vendor", "vibecoding-standard"))
        self.assertEqual(rc, 0)

    def test_legacy_vendor_refused_with_detection(self):
        """旧 v1.2.7 vendor 作为 --standard → rc1 + LEGACY_DETECTED，不写文件。"""
        p = subprocess.run(["git", "-C", REPO, "archive", "cfc083d", "vibecoding/vendor/vibecoding-standard"],
                           capture_output=True, stdin=subprocess.DEVNULL)
        if p.returncode != 0:
            self.skipTest("NOT_RUN: 无 cfc083d 历史，无法取得 v1.2.7 vendor")
        dest = os.path.join(self.tmp, "old")
        with tarfile.open(fileobj=io.BytesIO(p.stdout)) as tf:
            if sys.version_info >= (3, 12):
                tf.extractall(dest, filter="data")
            else:
                tf.extractall(dest)
        std = os.path.join(dest, "vibecoding", "vendor", "vibecoding-standard")
        before = snapshot(self.proj)
        rc, out = self.init("--apply", "--update-block", "--standard", std)
        self.assertEqual(rc, 1, out)
        self.assertIn("LEGACY_DETECTED", out)
        self.assertEqual(snapshot(self.proj), before)

    def test_no_upgrade_flag(self):
        buf = io.StringIO()
        import contextlib
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
            try:
                vb_init.main(["--help"])
            except SystemExit:
                pass
        self.assertNotIn("--upgrade", buf.getvalue())
        err = io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as cm:
                vb_init.main(["--project", self.proj, "--upgrade"])
        self.assertEqual(cm.exception.code, 2)
        self.assertIn("unrecognized arguments: --upgrade", err.getvalue())
        self.assertEqual(os.listdir(self.proj), [])


if __name__ == "__main__":
    unittest.main()
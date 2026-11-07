# -*- coding: utf-8 -*-
"""受管块归属判据回归测试。

`--update-block` 只授权升级**可证明由工具生成**的陈旧受管块：内容必须逐字等于冻结模板 × 已发布工具版本 ×
已知标准版本 × 冻结声明 × 工具独立得到的规范定位的渲染结果。用户修改或来源无法证明的内容一律
USER_MODIFIED / USER_MODIFIED_OR_UNKNOWN、NEED_DECISION、rc=2、零写入；每个场景都以字节快照证明未被覆盖。
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import unittest
from unittest import mock

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from test_vb_init import snapshot, vb_init, block_of  # noqa: E402
from test_s_skill_01 import Mig, rd, wr, rb, OLD, NEW, REPO  # noqa: E402

LEGACY_TEMPLATE_SHA256 = "cc8882721d097a8bd1f1f54a4ed9ce10612a52e0f1703f9c691b7c130f7adf43"
SKIP_MARK = "使用了 --skip-standard-check"
SECRET = "SECRET_TOKEN=vbtest-do-not-echo-7f3a"
AG = "AGENTS.md"
CP = os.path.join(".vibecoding", "AGENTS.block.md")


class Own(Mig):
    def p(self, rel):
        return os.path.join(self.proj, rel)

    def edit_block(self, line=SECRET):
        t = rd(self.p(AG), newline="")
        i = t.index(vb_init.END)
        wr(self.p(AG), t[:i] + line + "\n" + t[i:], newline="")

    def edit_copy(self, line=SECRET):
        t = rd(self.p(CP), newline="")
        i = t.index(vb_init.END)
        wr(self.p(CP), t[:i] + line + "\n" + t[i:], newline="")

    def assert_refused(self, expect_files, cls=None):
        """所有授权组合下：rc2、NEED_DECISION、零写入（字节快照）、user_modified 结构化输出、不回显用户内容。"""
        before = snapshot(self.proj)
        for extra in ((), ("--update-block",), ("--update-block", "--allow-dirty")):
            for mode in ((), ("--apply",)):
                rc, out = self.init(*(mode + extra))
                self.assertEqual(rc, 2, out)
                self.assertIn("NEED_DECISION / CONFLICT", out)
                self.assertNotIn("would_", out, "被阻断的 dry-run 不得显示 would_*")
                self.assertNotIn(SECRET, out, "冲突差异不得回显用户内容")
                self.assertIn("USER_MODIFIED", out)
                self.assertIn("人工处置", out)
                self.assertEqual(snapshot(self.proj), before, "用户文件必须逐字节未被覆盖")
                rc, j = self.init_json(*(mode + extra))
                self.assertEqual(rc, 2)
                self.assertEqual(j["rc"], 2)
                self.assertEqual(j["plan"]["write_set"], [])
                self.assertFalse(any(s.get("write") for s in j["steps"]))
                um = j["plan"]["user_modified"]
                self.assertEqual(sorted(u["file"] for u in um), sorted(expect_files))
                for u in um:
                    self.assertTrue(u["path"] and u["reason"])
                    self.assertIn(u["classification"], ("USER_MODIFIED", "USER_MODIFIED_OR_UNKNOWN"))
                    if cls:
                        self.assertEqual(u["classification"], cls)
                self.assertTrue(j["plan"]["manual_guidance"])
                self.assertNotIn(SECRET, json.dumps(j, ensure_ascii=False))
                self.assertEqual(snapshot(self.proj), before)
        return before


BLK = "AGENTS.md 标记块"
CPY = ".vibecoding/AGENTS.block.md"


class TestFrozenTemplate(unittest.TestCase):
    def test_legacy_template_hash_pinned(self):
        t = vb_init.LEGACY_BLOCK_TEMPLATE_V127
        self.assertEqual(hashlib.sha256(t.encode("utf-8")).hexdigest(), LEGACY_TEMPLATE_SHA256)
        self.assertEqual(vb_init.LEGACY_BLOCK_TEMPLATE_V127_SHA256, LEGACY_TEMPLATE_SHA256)

    def test_legacy_template_equals_released_history(self):
        p = subprocess.run(["git", "-C", REPO, "show", "19f83be:vibecoding/scripts/vb_init.py"],
                           capture_output=True, stdin=subprocess.DEVNULL)
        if p.returncode != 0:
            self.skipTest("NOT_RUN: 无 19f83be 历史")
        src = p.stdout.decode("utf-8").replace("\r\n", "\n")
        i = src.index('\nBLOCK = """') + len('\nBLOCK = """')
        self.assertEqual(src[i:src.index('"""', i)], vb_init.LEGACY_BLOCK_TEMPLATE_V127)

    def test_no_content_derived_trust(self):
        self.assertFalse(hasattr(vb_init, "_rerender_matches"))
        self.assertFalse(hasattr(vb_init, "RESOLVED_RE"))


class TestScenarios(Own):
    def test_s01_legacy_pristine_no_auth_rc2_zero_writes(self):
        self.make_legacy()
        before = snapshot(self.proj)
        for mode in ((), ("--apply",)):
            rc, out = self.init(*mode)
            self.assertEqual(rc, 2, out)
            self.assertNotIn("would_", out)
        self.assertEqual(snapshot(self.proj), before)

    def test_s02_legacy_pristine_authorized_rc0_consistent(self):
        self.make_legacy()
        rc, out = self.init("--apply", "--update-block")
        self.assertEqual(rc, 0, out)
        self.assert_consistent()

    def test_s02b_legacy_skip_claim_is_tool_generated(self):
        """v1.2.7 以 --skip-standard-check 生成的块同样属于可信契约 → 授权可升级。"""
        rc, out = self.init("--apply", "--skip-standard-check")
        self.assertEqual(rc, 0, out)
        for rel in (AG, CP):
            wr(self.p(rel), rd(self.p(rel), newline="").replace(NEW, OLD), newline="")
        rc, out = self.init("--apply")
        self.assertEqual(rc, 2, out)
        rc, out = self.init("--apply", "--update-block")
        self.assertEqual(rc, 0, out)
        self.assert_consistent()

    def test_s03_legacy_identical_edit_block_and_copy_refused(self):
        """块与副本被改成相同内容：不得据“块 == 副本”推断未修改。"""
        self.make_legacy()
        self.edit_block()
        self.edit_copy()
        self.assertEqual(vb_init.normalize(block_of(self.proj)), vb_init.normalize(rd(self.p(CP))))
        self.assert_refused([BLK, CPY], "USER_MODIFIED")
        self.assertIn(SECRET, rd(self.p(AG)))
        self.assertIn(SECRET, rd(self.p(CP)))

    def test_s03b_current_identical_edit_refused(self):
        self.assertEqual(self.init("--apply")[0], 0)
        self.edit_block()
        self.edit_copy()
        self.assert_refused([BLK, CPY], "USER_MODIFIED")

    def test_s04_legacy_block_only_edit(self):
        self.make_legacy()
        self.edit_block()
        self.assert_refused([BLK])

    def test_s05_legacy_copy_only_edit(self):
        self.make_legacy()
        self.edit_copy()
        self.assert_refused([CPY])

    def test_s06_current_block_only_edit_even_with_update_block(self):
        self.assertEqual(self.init("--apply")[0], 0)
        self.edit_block()
        self.assert_refused([BLK], "USER_MODIFIED")

    def test_s07_current_copy_only_edit_even_with_update_block(self):
        self.assertEqual(self.init("--apply")[0], 0)
        self.edit_copy()
        self.assert_refused([CPY], "USER_MODIFIED")

    def test_s08_unidentifiable_content_refused(self):
        self.assertEqual(self.init("--apply")[0], 0)
        t = rd(self.p(AG), newline="")
        s, e = vb_init.split_block(t)
        wr(self.p(AG), t[:s] + vb_init.BEGIN + " 自定义 -->\n" + SECRET + "\n" + vb_init.END + t[e:], newline="")
        self.assert_refused([BLK], "USER_MODIFIED_OR_UNKNOWN")

    def test_s08b_unknown_version_header_refused(self):
        self.assertEqual(self.init("--apply")[0], 0)
        for rel in (AG, CP):
            wr(self.p(rel), rd(self.p(rel), newline="").replace("standard=" + NEW, "standard=9.9.9"), newline="")
        self.assert_refused([BLK, CPY], "USER_MODIFIED_OR_UNKNOWN")

    def test_s08c_self_consistent_rerender_with_foreign_path_refused(self):
        """内容按模板自洽、但规范路径取自内容本身（非工具独立得到）→ 不可信。"""
        self.make_legacy()
        vp = vb_init.vendor_reference(self.proj, vb_init.find_standard(self.proj, None)[0])["path"]
        for rel in (AG, CP):
            wr(self.p(rel), rd(self.p(rel), newline="").replace("`%s`" % vp, "`elsewhere/evil-standard`"), newline="")
        self.assert_refused([BLK, CPY], "USER_MODIFIED")

    def test_s09_init_and_repeat_idempotent(self):
        self.write("AGENTS.md", "# 用户规则\n")
        self.assertEqual(self.init("--apply")[0], 0)
        snap = snapshot(self.proj)
        for extra in ((), ("--update-block",)):
            rc, out = self.init("--apply", *extra)
            self.assertEqual(rc, 0, out)
            self.assertEqual(snapshot(self.proj), snap)

    def test_s10_dry_run_matches_apply(self):
        for setup, auth, exp_rc in ((lambda: self.make_legacy(), ("--update-block",), 0),
                                    (lambda: self.make_legacy(), (), 2),
                                    (lambda: (self.make_legacy(), self.edit_block()), ("--update-block",), 2)):
            self.tearDown(); self.setUp()
            setup()
            rc_d, j = self.init_json(*auth)
            before = snapshot(self.proj)
            rc_a, _ = self.init("--apply", *auth)
            after = snapshot(self.proj)
            self.assertEqual((rc_d, rc_a), (exp_rc, exp_rc))
            changed = {k for k in set(before) | set(after) if before.get(k) != after.get(k)}
            self.assertEqual(changed, set(j["plan"]["write_set"]))
            if exp_rc == 2:
                self.assertFalse(any(str(s.get("status", "")).startswith("would_")
                                     or str(s.get("action", "")).startswith("would_") for s in j["steps"]))

    def test_s11_injected_write_failure_rolls_back(self):
        self.make_legacy()
        before = snapshot(self.proj)
        real = vb_init._replace

        def rep(src, dst):
            if os.path.basename(dst) == "AGENTS.md":
                raise OSError(28, "injected")
            return real(src, dst)
        with mock.patch.object(vb_init, "_replace", rep):
            rc, out = self.init("--apply", "--update-block")
        self.assertEqual(rc, 1, out)
        self.assertEqual(snapshot(self.proj), before)

    def test_s12_bytes_outside_markers_and_other_files_preserved(self):
        self.write("AGENTS.md", "# 前缀\r\n用户内容\r\n")
        self.assertEqual(self.init("--apply")[0], 0)
        with open(self.p(AG), "ab") as fh:
            fh.write(b"\r\n## \xe5\x90\x8e\xe7\xbc\x80\r\ntail-bytes\r\n")
        self.write("notes.txt", "其他文件\n")
        for rel in (AG, CP):
            wr(self.p(rel), rd(self.p(rel), newline="").replace(NEW, OLD), newline="")
        raw = rb(self.p(AG))
        t = raw.decode("utf-8")
        s, e = vb_init.split_block(t)
        pre, post = t[:s].encode("utf-8"), t[e:].encode("utf-8")
        other = {k: v for k, v in snapshot(self.proj).items() if k not in (AG, CP.replace(os.sep, "/"))
                 and not k.startswith(".vibecoding")}
        rc, out = self.init("--apply", "--update-block", "--allow-dirty")
        self.assertEqual(rc, 0, out)
        t2 = rb(self.p(AG)).decode("utf-8")
        s2, e2 = vb_init.split_block(t2)
        self.assertEqual(t2[:s2].encode("utf-8"), pre)
        self.assertEqual(t2[e2:].encode("utf-8"), post)
        after = snapshot(self.proj)
        for k, v in other.items():
            self.assertEqual(after.get(k), v, k)


class TestLimitedDiff(unittest.TestCase):
    def test_hides_user_lines_and_caps_length(self):
        exp = "a\nb\nc\n"
        act = "a\n" + "\n".join("%s-%d" % (SECRET, i) for i in range(40)) + "\nc\n"
        d = vb_init.limited_diff(exp, act, "X")
        self.assertNotIn(SECRET, "\n".join(d))
        self.assertLessEqual(len(d), vb_init.DIFF_MAX_LINES + 2)
        self.assertIn("sha256:", "\n".join(d))
        self.assertIn("已省略", d[-1])



class TestConfigPathNotTrusted(Own):
    """N1：可编辑 config.standard_vendor_path 不得参与可信渲染（R16 recheck T1/T2/T2a/T3）。"""

    SECRET2 = "R16RC_SECRET_do-not-echo-91c2"
    RESOLVED = "**本次初始化解算**："

    def _vref_path(self):
        return vb_init.vendor_reference(self.proj, vb_init.find_standard(self.proj, None)[0])["path"]

    def _cond(self):
        return vb_init.vendor_reference(self.proj, vb_init.find_standard(self.proj, None)[0])["condition"]

    def _set_cfg_path(self, path):
        p = self.p(os.path.join(".vibecoding", "config.json"))
        cfg = json.loads(rd(p))
        cfg["standard_vendor_path"] = path
        wr(p, json.dumps(cfg, ensure_ascii=False, indent=2) + "\n")

    def _inj_line_after_resolved(self, text):
        nl = "\r\n" if "\r\n" in text else "\n"
        lines = text.split(nl)
        k = [i for i, l in enumerate(lines) if self.RESOLVED in l][0]
        inj = "  - **团队私有约定**：" + self.SECRET2 + " `x`（" + self._cond() + "）。"
        return nl.join(lines[: k + 1] + [inj] + lines[k + 1:])

    def test_t1_custom_path_in_block_copy_and_config_refused(self):
        """三处路径改成同一自定义值：不得因 config 记录而判 STALE。"""
        self.assertEqual(self.init("--apply")[0], 0)
        custom = "D:/team/custom-standard" if os.name == "nt" else "/team/custom-standard"
        vp = self._vref_path()
        for rel in (AG, CP):
            wr(self.p(rel), rd(self.p(rel), newline="").replace("`%s`" % vp, "`%s`" % custom), newline="")
        self._set_cfg_path(custom)
        before = snapshot(self.proj)
        self.assert_refused([BLK, CPY], "USER_MODIFIED")
        self.assertEqual(snapshot(self.proj), before)

    def test_t2_crafted_config_path_with_injected_line_block_and_copy(self):
        """config 路径被拼进用户行，使「用 config 路径重渲染」会包含 SECRET → 必须拒绝。"""
        self.assertEqual(self.init("--apply")[0], 0)
        for rel in (AG, CP):
            wr(self.p(rel), self._inj_line_after_resolved(rd(self.p(rel), newline="")), newline="")
        inj_path = self._vref_path() + "`（" + self._cond() + "）。\n  - **团队私有约定**：" + self.SECRET2 + " `x"
        self._set_cfg_path(inj_path)
        before = snapshot(self.proj)
        for extra in ((), ("--update-block",), ("--update-block", "--allow-dirty")):
            for mode in ((), ("--apply",)):
                rc, out = self.init(*(mode + extra))
                self.assertEqual(rc, 2, out)
                self.assertIn("USER_MODIFIED", out)
                self.assertNotIn(self.SECRET2, out)
                self.assertNotIn("would_", out)
                self.assertEqual(snapshot(self.proj), before)
                self.assertIn(self.SECRET2, rd(self.p(AG)))
                self.assertIn(self.SECRET2, rd(self.p(CP)))

    def test_t2a_crafted_config_path_block_only(self):
        """仅改块 + 篡改 config；副本原样。"""
        self.assertEqual(self.init("--apply")[0], 0)
        wr(self.p(AG), self._inj_line_after_resolved(rd(self.p(AG), newline="")), newline="")
        inj_path = self._vref_path() + "`（" + self._cond() + "）。\n  - **团队私有约定**：" + self.SECRET2 + " `x"
        self._set_cfg_path(inj_path)
        before = snapshot(self.proj)
        rc, out = self.init("--apply", "--update-block")
        self.assertEqual(rc, 2, out)
        self.assertIn("USER_MODIFIED", out)
        self.assertNotIn(self.SECRET2, out)
        self.assertEqual(snapshot(self.proj), before)
        self.assertIn(self.SECRET2, rd(self.p(AG)))

    def test_t3_legacy_crafted_config_path(self):
        """v1.2.7 legacy 身份 + 同上注入。"""
        self.make_legacy()
        for rel in (AG, CP):
            wr(self.p(rel), self._inj_line_after_resolved(rd(self.p(rel), newline="")), newline="")
        inj_path = self._vref_path() + "`（" + self._cond() + "）。\n  - **团队私有约定**：" + self.SECRET2 + " `x"
        self._set_cfg_path(inj_path)
        before = snapshot(self.proj)
        rc, out = self.init("--apply", "--update-block")
        self.assertEqual(rc, 2, out)
        self.assertIn("USER_MODIFIED", out)
        self.assertEqual(snapshot(self.proj), before)
        self.assertIn(self.SECRET2, rd(self.p(AG)))


class TestOwnershipProofHardening(Own):
    """针对性抓住从被测内容自证的变异（M2b/M2c/M6）及过度归一化（M5）。"""

    def test_skill_header_only_change_refused(self):
        """只改块头 skill=（其余不变）→ 不得因「换成当前 skill 再比对」而信任（杀 M2b）。"""
        self.assertEqual(self.init("--apply")[0], 0)
        for rel in (AG, CP):
            t = rd(self.p(rel), newline="")
            wr(self.p(rel), t.replace("skill=" + vb_init.SKILL_VERSION, "skill=9.9.9", 1), newline="")
        self.assert_refused([BLK, CPY], "USER_MODIFIED")

    def test_path_line_only_in_block_refused(self):
        """仅块内改解算路径行（副本未改）→ 拒绝（加强 M2/M2c）。"""
        self.assertEqual(self.init("--apply")[0], 0)
        vp = vb_init.vendor_reference(self.proj, vb_init.find_standard(self.proj, None)[0])["path"]
        wr(self.p(AG), rd(self.p(AG), newline="").replace("`%s`" % vp, "`elsewhere/evil-standard`"), newline="")
        self.assert_refused([BLK], "USER_MODIFIED")

    def test_internal_whitespace_change_refused(self):
        """行内插入空格（非行尾）不得被过度 normalize 吞掉（杀 M5 类）。"""
        self.assertEqual(self.init("--apply")[0], 0)
        t = rd(self.p(AG), newline="")
        # insert space inside a word that exists in the block
        self.assertIn("工程纪律", t)
        wr(self.p(AG), t.replace("工程纪律", "工程 纪律", 1), newline="")
        self.assert_refused([BLK], "USER_MODIFIED")

    def test_standard_header_only_change_refused(self):
        """只改块头 standard=（杀「忽略头行再比对」M6）。"""
        self.assertEqual(self.init("--apply")[0], 0)
        for rel in (AG, CP):
            t = rd(self.p(rel), newline="")
            wr(self.p(rel), t.replace("standard=" + NEW, "standard=9.9.9", 1), newline="")
        self.assert_refused([BLK, CPY], "USER_MODIFIED_OR_UNKNOWN")

    def test_no_recorded_path_helper(self):
        """实现层：trusted_renderings 只接受 vref；无 _vendor_refs / recorded_path。"""
        import inspect
        src = inspect.getsource(vb_init)
        self.assertNotIn("def _vendor_refs", src)
        self.assertNotIn("recorded_path", src)
        sig = inspect.signature(vb_init.trusted_renderings)
        self.assertEqual(list(sig.parameters), ["vref"])

if __name__ == "__main__":
    unittest.main()

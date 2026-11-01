# -*- coding: utf-8 -*-
"""vb_gate 的 R4-N7 / R9-F1 信任边界测试。

被测脚本默认是本仓库 vibecoding/scripts/vb_gate.py；设置 VB_GATE_UNDER_TEST 可指向其他版本（判别 / 变异）。
全部在系统临时目录进行，不触碰真实技能目录。
"""
import contextlib
import hashlib
import importlib.util
import io
import os
import py_compile
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
VENDOR = os.path.join(REPO, "vibecoding", "vendor", "vibecoding-standard")
GATE = os.environ.get("VB_GATE_UNDER_TEST") or os.path.join(REPO, "vibecoding", "scripts", "vb_gate.py")

EVIL = '''import os, sys
open(os.environ["VB_TEST_MARKER"], "w").write("executed")
sys.exit(0)
'''


def crafted_standard(root):
    """R9 复现：自洽篡改的标准目录——check_evidence.py 写标记并返回 0，MANIFEST 同步改写（自带校验会 PASS）。"""
    std = os.path.join(root, "crafted-standard")
    shutil.copytree(VENDOR, std)
    ce = os.path.join(std, "tools", "check_evidence.py")
    data = EVIL.encode("utf-8")
    with open(ce, "wb") as fh:
        fh.write(data)
    man = os.path.join(std, "MANIFEST.sha256")
    with open(man, "rb") as fh:
        lines = fh.read().decode("utf-8").splitlines(True)
    hit = 0
    for i, line in enumerate(lines):
        if line.rstrip().endswith("tools/check_evidence.py"):
            lines[i] = hashlib.sha256(data).hexdigest() + line[64:]
            hit += 1
    assert hit == 1, "场景前提：清单中有且仅有一行 tools/check_evidence.py"
    with open(man, "wb") as fh:
        fh.write("".join(lines).encode("utf-8"))
    r = subprocess.run([sys.executable, os.path.join(std, "tools", "verify_manifest.py")], cwd=std,
                       capture_output=True)
    assert r.returncode == 0, "场景前提：自洽篡改目录的自带校验应 PASS"
    return std


class GateTrustBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="vbgate_")
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.proj = os.path.join(self.tmp, "proj")
        os.makedirs(self.proj)
        self.marker = os.path.join(self.tmp, "MARKER")
        self.ok = os.path.join(self.tmp, "ok.py")
        with open(self.ok, "w") as fh:
            fh.write("import sys\nsys.exit(0)\n")

    def gate(self, *args, env_extra=None):
        env = dict(os.environ)
        env.pop("VB_STANDARD_HOME", None)
        env["VB_TEST_MARKER"] = self.marker
        env["PYTHONIOENCODING"] = "utf-8"
        if env_extra:
            env.update(env_extra)
        cmd = [sys.executable, GATE, "--project", self.proj, "--task", "T1",
               "--verify", '"%s" "%s"' % (sys.executable, self.ok), *args]
        r = subprocess.run(cmd, capture_output=True, env=env, cwd=self.proj, timeout=300)
        return r.returncode, (r.stdout + r.stderr).decode("utf-8", "replace")

    def evidence(self):
        with open(os.path.join(self.proj, ".vibecoding", "evidence", "T1.md"), encoding="utf-8") as fh:
            return fh.read()


class TestR9F1GateTrustBoundary(GateTrustBase):
    def test_crafted_standard_via_flag_not_executed_and_not_pass(self):
        std = crafted_standard(self.tmp)
        rc, out = self.gate("--standard", std)
        self.assertFalse(os.path.exists(self.marker), "未经固定清单校验的 check_evidence.py 被执行了:\n" + out)
        self.assertNotEqual(rc, 0, out)
        self.assertNotIn("门禁: PASS", out)
        self.assertIn("信任边界", out)
        self.assertIn("结构校验=FAIL", out)   # R10-N5/F1b：拒绝记 FAIL，不是 UNKNOWN

    def test_crafted_standard_via_env_not_executed_and_not_pass(self):
        std = crafted_standard(self.tmp)
        rc, out = self.gate(env_extra={"VB_STANDARD_HOME": std})
        self.assertFalse(os.path.exists(self.marker), "VB_STANDARD_HOME 指向的未校验脚本被执行了:\n" + out)
        self.assertNotEqual(rc, 0, out)
        self.assertNotIn("门禁: PASS", out)

    def test_check_standard_failure_recorded_and_not_executed(self):
        std = crafted_standard(self.tmp)
        rc, out = self.gate("--standard", std, "--check-standard")
        self.assertFalse(os.path.exists(self.marker), out)
        self.assertEqual(rc, 1, out)
        self.assertIn("| AC-001 | `vb_trust 固定清单校验` | 1 | FAIL |", self.evidence())

    def test_real_vendor_copy_via_flag_still_runs_structure_check(self):
        std = os.path.join(self.tmp, "real-standard")
        shutil.copytree(VENDOR, std)
        rc, out = self.gate("--standard", std, "--check-standard")
        self.assertIn("| AC-001 | `vb_trust 固定清单校验` | 0 | PASS |", self.evidence())
        self.assertNotIn("信任边界", out)
        self.assertIn("标准证据门禁（check_evidence.py）", out)


def plant_pyc(std, modname):
    """R10-N1 复现：在 tools/ 放无源 .pyc（被同目录脚本 import 时执行）。"""
    src = os.path.join(std, "..", "evil_%s.py" % modname)
    with open(src, "w", encoding="utf-8") as fh:
        fh.write(EVIL)
    py_compile.compile(src, cfile=os.path.join(std, "tools", modname + ".pyc"), doraise=True)


def real_copy(root, name="pyc-standard"):
    std = os.path.join(root, name)
    shutil.copytree(VENDOR, std, ignore=shutil.ignore_patterns("__pycache__"))
    return std


def load_gate():
    spec = importlib.util.spec_from_file_location("vb_gate_under_test_%d" % id(object()), GATE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestR10N1PycPlants(GateTrustBase):
    def assert_blocked(self, rc, out):
        self.assertFalse(os.path.exists(self.marker), "植入的 .pyc 被执行了:\n" + out)
        self.assertNotEqual(rc, 0, out)
        self.assertNotIn("门禁: PASS", out)
        self.assertIn("结构校验=FAIL", out)

    def test_argparse_pyc_via_flag(self):
        std = real_copy(self.tmp)
        plant_pyc(std, "argparse")
        self.assert_blocked(*self.gate("--standard", std))

    def test_datetime_pyc_via_flag(self):
        std = real_copy(self.tmp)
        plant_pyc(std, "datetime")
        self.assert_blocked(*self.gate("--standard", std))

    def test_pyc_via_env(self):
        std = real_copy(self.tmp)
        plant_pyc(std, "argparse")
        self.assert_blocked(*self.gate(env_extra={"VB_STANDARD_HOME": std}))

    def test_pyc_via_relative_flag(self):
        std = real_copy(self.proj, "rel-std")
        plant_pyc(std, "argparse")
        self.assert_blocked(*self.gate("--standard", "rel-std"))

    def test_pyc_with_check_standard(self):
        std = real_copy(self.tmp)
        plant_pyc(std, "argparse")
        rc, out = self.gate("--standard", std, "--check-standard")
        self.assert_blocked(rc, out)
        self.assertIn("| AC-001 | `vb_trust 固定清单校验` | 1 | FAIL |", self.evidence())

    def test_pyc_via_project_vendor_fallback(self):
        skill = os.path.join(self.tmp, "skill", "scripts")
        os.makedirs(skill)
        shutil.copy(GATE, os.path.join(skill, "vb_gate.py"))
        shutil.copy(os.path.join(os.path.dirname(GATE), "vb_trust.py"), skill)
        std = real_copy(os.path.join(self.proj, ".vibecoding", "vendor"), "vibecoding-standard")
        plant_pyc(std, "argparse")
        env = dict(os.environ, VB_TEST_MARKER=self.marker, PYTHONIOENCODING="utf-8")
        env.pop("VB_STANDARD_HOME", None)
        r = subprocess.run([sys.executable, os.path.join(skill, "vb_gate.py"), "--project", self.proj, "--task", "T1",
                            "--verify", '"%s" "%s"' % (sys.executable, self.ok)],
                           capture_output=True, env=env, cwd=self.proj, timeout=300)
        out = (r.stdout + r.stderr).decode("utf-8", "replace")
        # 技能副本无 vendor，唯一候选是项目回落目录；assert_blocked 要求“结构校验=FAIL”即证明该目录被定位并拒绝
        self.assert_blocked(r.returncode, out)


class TestR10TrustWalk(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="vbtrust_")
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.std = real_copy(self.tmp)
        spec = importlib.util.spec_from_file_location("vb_trust_t", os.path.join(os.path.dirname(GATE), "vb_trust.py"))
        self.trust = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.trust)

    def put(self, rel, data=b"x"):
        p = os.path.join(self.std, *rel.split("/"))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as fh:
            fh.write(data)

    def test_clean_copy_passes(self):
        self.assertEqual(self.trust.verify_pinned(self.std)[0], 0)

    def test_pyc_outside_pycache_is_unlisted(self):
        self.put("tools/argparse.pyc")
        rc, lines = self.trust.verify_pinned(self.std)
        self.assertEqual(rc, 1, lines)
        self.assertIn("!! 未登记文件: tools/argparse.pyc", lines)

    def test_extra_py_in_tools_is_unlisted(self):   # R10-N5/F1f
        self.put("tools/argparse.py", b"print(1)\n")
        rc, lines = self.trust.verify_pinned(self.std)
        self.assertEqual(rc, 1, lines)
        self.assertIn("!! 未登记文件: tools/argparse.py", lines)

    def test_pycache_tolerated_by_design(self):
        # 文档化决定：__pycache__ 不参与信任也不被使用（vb_gate 只跑私有副本，-I -B）
        self.put("tools/__pycache__/check_evidence.cpython-399.pyc")
        self.assertEqual(self.trust.verify_pinned(self.std)[0], 0)

    def test_read_verified(self):
        self.assertIsNotNone(self.trust.read_verified(self.std, "tools/check_evidence.py"))
        self.put("tools/check_evidence.py", b"tampered\n")
        self.assertIsNone(self.trust.read_verified(self.std, "tools/check_evidence.py"))


class TestR10N2Toctou(GateTrustBase):
    def test_swap_after_verification_not_executed(self):
        std = real_copy(self.tmp)
        mod = load_gate()
        real = mod.vb_trust.verify_pinned

        def verify_then_swap(d):
            res = real(d)
            with open(os.path.join(std, "tools", "check_evidence.py"), "w", encoding="utf-8") as fh:
                fh.write(EVIL)
            return res
        buf = io.StringIO()
        with mock.patch.object(mod.vb_trust, "verify_pinned", verify_then_swap), \
                mock.patch.dict(os.environ, {"VB_TEST_MARKER": self.marker}), contextlib.redirect_stdout(buf):
            rc = mod.main(["--project", self.proj, "--task", "T1", "--standard", std,
                           "--verify", '"%s" "%s"' % (sys.executable, self.ok)])
        out = buf.getvalue()
        self.assertFalse(os.path.exists(self.marker), "校验后被替换的脚本被执行了:\n" + out)
        self.assertEqual(rc, 1, out)
        self.assertIn("结构校验=FAIL", out)


class TestR10N4GateInterrupt(unittest.TestCase):
    def test_keyboard_interrupt_diagnostic(self):
        r = subprocess.run([sys.executable, "-c",
                            "import runpy,sys,builtins\n"
                            "sys.argv=[%r,'--task','T1','--project',%r]\n"
                            "import argparse\n"
                            "def boom(*a,**k): raise KeyboardInterrupt\n"
                            "argparse.ArgumentParser.parse_args=boom\n"
                            "runpy.run_path(%r, run_name='__main__')\n" % (GATE, tempfile.gettempdir(), GATE)],
                           capture_output=True, env=dict(os.environ, PYTHONIOENCODING="utf-8"), timeout=120)
        out = (r.stdout + r.stderr).decode("utf-8", "replace")
        self.assertEqual(r.returncode, 130, out)
        self.assertIn("INTERRUPTED", out)
        self.assertNotIn("Traceback", out)


class TestR10GitAttributes(unittest.TestCase):
    """R10-N5/F2a/F2b：换行策略自动化检查（内容 + git check-attr）。"""
    def test_gitattributes_lines(self):
        with open(os.path.join(REPO, ".gitattributes"), encoding="utf-8") as fh:
            lines = [l.strip() for l in fh if l.strip() and not l.lstrip().startswith("#")]
        self.assertIn("* text=auto eol=lf", lines)
        self.assertIn("vibecoding/vendor/** -text", lines)

    def test_check_attr(self):
        if not os.path.isdir(os.path.join(REPO, ".git")) or shutil.which("git") is None:
            self.skipTest("非 git 检出")
        r = subprocess.run(["git", "-C", REPO, "check-attr", "text", "eol", "--",
                            "vibecoding/vendor/vibecoding-standard/MANIFEST.sha256", "tools/install_skill.py"],
                           capture_output=True, text=True)
        out = r.stdout
        self.assertIn("vibecoding/vendor/vibecoding-standard/MANIFEST.sha256: text: unset", out)
        self.assertIn("tools/install_skill.py: text: auto", out)
        self.assertIn("tools/install_skill.py: eol: lf", out)


if __name__ == "__main__":
    unittest.main()
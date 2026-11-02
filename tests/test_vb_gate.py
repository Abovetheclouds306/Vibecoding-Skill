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
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))


# R11-N6：测试不得在工作树生成 __pycache__（含子进程），临时目录必须真正删除（git 只读对象也删），残留即报错。
sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"


def _rm_tree(path):
    def onerr(func, p, exc):
        try:
            os.chmod(p, stat.S_IWRITE)
            func(p)
        except OSError:
            pass
    if sys.version_info >= (3, 12):
        shutil.rmtree(path, onexc=onerr)
    else:
        shutil.rmtree(path, onerror=onerr)
    if os.path.exists(path):
        raise AssertionError("测试临时目录未清理: %s" % path)
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
    r = subprocess.run([sys.executable, "-B", os.path.join(std, "tools", "verify_manifest.py")], cwd=std,
                       capture_output=True)
    assert r.returncode == 0, "场景前提：自洽篡改目录的自带校验应 PASS"
    return std


class GateTrustBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="vbgate_")
        self.addCleanup(_rm_tree, self.tmp)
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
        self.addCleanup(_rm_tree, self.tmp)
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

    def test_read_verified_requires_pinned_manifest(self):   # 杀“只比对清单登记值、不比对固定清单”
        import hashlib
        data = b"tampered\n"
        self.put("tools/check_evidence.py", data)
        mp = os.path.join(self.std, "MANIFEST.sha256")
        with open(mp, "rb") as fh:
            lines = fh.read().decode("utf-8").splitlines()
        new = [("%s  tools/check_evidence.py" % hashlib.sha256(data).hexdigest())
               if l.strip().endswith("tools/check_evidence.py") else l for l in lines]
        with open(mp, "wb") as fh:
            fh.write(("\n".join(new) + "\n").encode("utf-8"))
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


class TestR11ExecIsolation(GateTrustBase):
    """纵深防御：即使信任校验被绕过（mock 为通过），执行也只用私有副本 + -I -B。"""
    def run_bypassed(self, std, env):
        mod = load_gate()
        buf = io.StringIO()
        with mock.patch.object(mod.vb_trust, "verify_pinned", lambda d: (0, [])), \
                mock.patch.dict(os.environ, dict(env, VB_TEST_MARKER=self.marker)), contextlib.redirect_stdout(buf):
            rc = mod.main(["--project", self.proj, "--task", "T1", "--standard", std,
                           "--verify", '"%s" "%s"' % (sys.executable, self.ok)])
        return rc, buf.getvalue()

    def test_located_dir_pyc_not_used_even_if_trust_bypassed(self):
        std = real_copy(self.tmp)
        plant_pyc(std, "argparse")
        rc, out = self.run_bypassed(std, {})
        self.assertFalse(os.path.exists(self.marker), "被定位目录的 .pyc 被执行了:\n" + out)
        self.assertIn("门禁: PASS", out)   # 正对照：私有副本确实运行且正常

    def test_pythonpath_ignored_by_isolated_mode(self):
        std = real_copy(self.tmp)
        evil = os.path.join(self.tmp, "evilpath")
        os.makedirs(evil)
        with open(os.path.join(evil, "argparse.py"), "w", encoding="utf-8") as fh:
            fh.write("import os\nopen(os.environ['VB_TEST_MARKER'], 'w').close()\n")
        rc, out = self.run_bypassed(std, {"PYTHONPATH": evil})
        self.assertFalse(os.path.exists(self.marker), "PYTHONPATH 中的模块被导入了（未用 -I）:\n" + out)
        self.assertIn("门禁: PASS", out)


class TestR11SwapAfterRead(GateTrustBase):
    def test_swap_after_read_verified_not_executed(self):
        """杀“从被定位目录执行”：读取已核对字节之后再替换磁盘文件，执行的必须仍是已核对字节。"""
        std = real_copy(self.tmp)
        mod = load_gate()
        real = mod.vb_trust.read_verified

        def read_then_swap(d, rel):
            data = real(d, rel)
            with open(os.path.join(std, "tools", "check_evidence.py"), "w", encoding="utf-8") as fh:
                fh.write(EVIL)
            return data
        buf = io.StringIO()
        with mock.patch.object(mod.vb_trust, "read_verified", read_then_swap), \
                mock.patch.dict(os.environ, {"VB_TEST_MARKER": self.marker}), contextlib.redirect_stdout(buf):
            mod.main(["--project", self.proj, "--task", "T1", "--standard", std,
                      "--verify", '"%s" "%s"' % (sys.executable, self.ok)])
        out = buf.getvalue()
        self.assertFalse(os.path.exists(self.marker), "读取后被替换的磁盘文件被执行了:\n" + out)
        self.assertIn("门禁: PASS", out)


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
        # S-SKILL-01（Owner 批准方案 a）：v1.2.8 vendor 自带 .gitattributes（固定清单条目，
        # 不可删改），其 `* text=auto eol=lf` 依 git 就近优先规则覆盖根目录 `vibecoding/vendor/** -text`。
        # 因此不再断言 vendor `text: unset`，改为断言字节一致性的实际保障：eol=lf、无 CR 字节、*.zip binary。
        # 用 rev-parse 判定 git 检出，使 worktree（.git 为文件）也实际运行而非跳过。
        if shutil.which("git") is None:
            self.skipTest("无 git")
        chk = subprocess.run(["git", "-C", REPO, "rev-parse", "--is-inside-work-tree"],
                             capture_output=True, text=True)
        if chk.returncode != 0 or chk.stdout.strip() != "true":
            self.skipTest("非 git 检出")
        vend_rel = []
        for root, _dirs, files in os.walk(VENDOR):
            for f in files:
                full = os.path.join(root, f)
                with open(full, "rb") as fh:
                    self.assertNotIn(b"\r", fh.read(), "vendor 文件含 CR 字节: %s" % full)
                vend_rel.append(os.path.relpath(full, REPO).replace(os.sep, "/"))
        self.assertGreaterEqual(len(vend_rel), 38)
        zip_probe = "vibecoding/vendor/vibecoding-standard/probe.zip"
        # -z：NUL 分隔、路径不转义（避免 core.quotePath 对中文路径加引号转义）。
        r = subprocess.run(["git", "-C", REPO, "check-attr", "-z", "text", "eol", "diff", "binary", "--"]
                           + vend_rel + [zip_probe, "tools/install_skill.py"],
                           capture_output=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        parts = r.stdout.decode("utf-8").split("\0")
        attrs = {}
        for i in range(0, len(parts) - 2, 3):
            attrs[(parts[i], parts[i + 1])] = parts[i + 2]
        for rel in vend_rel:
            self.assertEqual(attrs.get((rel, "eol")), "lf", rel)
        self.assertEqual(attrs.get(("vibecoding/vendor/vibecoding-standard/MANIFEST.sha256", "eol")), "lf")
        self.assertEqual(attrs.get((zip_probe, "binary")), "set")
        self.assertEqual(attrs.get((zip_probe, "text")), "unset")
        self.assertEqual(attrs.get((zip_probe, "diff")), "unset")
        self.assertEqual(attrs.get(("tools/install_skill.py", "text")), "auto")
        self.assertEqual(attrs.get(("tools/install_skill.py", "eol")), "lf")


class TestR11N4RelativeEvidence(GateTrustBase):
    """R11-N4：相对 --evidence（ev.md / sub/ev.md）按 cwd 解析，不回溯、结构校验不因子进程 cwd 不同而 FAIL。"""
    def check(self, rel):
        rc, out = self.gate("--evidence", rel, "--standard", VENDOR)
        self.assertNotIn("Traceback", out)
        self.assertEqual(rc, 0, out)
        self.assertIn("门禁: PASS", out)
        self.assertTrue(os.path.isfile(os.path.join(self.proj, rel)), out)

    def test_bare_relative_file(self):
        self.check("ev.md")

    def test_relative_subdir_file(self):
        self.check(os.path.join("sub", "ev.md"))


class TestR11N2ChildIsolation(GateTrustBase):
    """R11-N2：check_evidence 子进程必须是 -I（不加载用户 site 的 usercustomize/.pth）；私有临时目录必须删除。"""
    def test_user_site_hooks_not_run_in_child(self):
        fake = os.path.join(self.tmp, "fakeuser")
        os.makedirs(fake)
        env = {"APPDATA": fake, "HOME": fake, "USERPROFILE": fake, "PYTHONUSERBASE": os.path.join(fake, "ub")}
        probe = subprocess.run([sys.executable, "-c", "import site;print(int(bool(site.ENABLE_USER_SITE)));print(site.getusersitepackages())"],
                               capture_output=True, env=dict(os.environ, **env), text=True)
        lines = probe.stdout.splitlines()
        if probe.returncode != 0 or not lines or lines[0] != "1":
            self.skipTest("NOT_RUN: 本解释器未启用用户 site")
        usp = lines[1]
        self.assertTrue(os.path.normcase(usp).startswith(os.path.normcase(fake)), usp)  # 绝不写真实用户 site
        os.makedirs(usp)
        m1 = os.path.join(self.tmp, "child_marker")
        m2 = os.path.join(self.tmp, "control_marker")
        hook = ("import os, sys\n"
                "open(%r, 'a').write('x')\n"
                "if 'check_evidence' in (sys.argv[0] if sys.argv else ''): open(%r, 'a').write('x')\n") % (m2, m1)
        with open(os.path.join(usp, "usercustomize.py"), "w") as fh:
            fh.write(hook)
        with open(os.path.join(usp, "vbtest.pth"), "w") as fh:
            fh.write("import os, sys; open(%r, 'a').write('p'); 'check_evidence' in (sys.argv[0] if sys.argv else '') and open(%r, 'a').write('p')\n" % (m2, m1))
        rc, out = self.gate("--standard", VENDOR, env_extra=env)
        self.assertTrue(os.path.exists(m2), "对照失败：用户 site 钩子未在任何进程中加载，测试无效\n" + out)
        self.assertFalse(os.path.exists(m1), "check_evidence 子进程加载了用户 site 钩子（应为 -I）\n" + out)
        self.assertEqual(rc, 0, out)
        self.assertIn("门禁: PASS", out)

    def leftovers(self, d):
        return [n for n in os.listdir(d) if n.startswith("vb_gate_std_")]

    def test_private_dir_removed(self):
        ttemp = os.path.join(self.tmp, "ttemp")
        os.makedirs(ttemp)
        env = {"TEMP": ttemp, "TMP": ttemp, "TMPDIR": ttemp}
        rc, out = self.gate("--standard", VENDOR, env_extra=env)
        self.assertEqual(rc, 0, out)
        self.assertIn("结构校验", out)
        self.assertEqual(self.leftovers(ttemp), [], out)

    def test_private_dir_removed_when_child_crashes(self):
        ttemp = os.path.join(self.tmp, "ttemp")
        os.makedirs(ttemp)
        env = {"TEMP": ttemp, "TMP": ttemp, "TMPDIR": ttemp}
        rc, out = self.gate("--standard", VENDOR, "--python", os.path.join(self.tmp, "no-such-python.exe"), env_extra=env)
        self.assertNotEqual(rc, 0, out)
        self.assertNotIn("门禁: PASS", out)
        self.assertEqual(self.leftovers(ttemp), [], out)


if __name__ == "__main__":
    unittest.main()
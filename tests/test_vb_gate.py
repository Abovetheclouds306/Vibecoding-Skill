# -*- coding: utf-8 -*-
"""vb_gate 的 R4-N7 / R9-F1 信任边界测试。

被测脚本默认是本仓库 vibecoding/scripts/vb_gate.py；设置 VB_GATE_UNDER_TEST 可指向其他版本（判别 / 变异）。
全部在系统临时目录进行，不触碰真实技能目录。
"""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

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


if __name__ == "__main__":
    unittest.main()
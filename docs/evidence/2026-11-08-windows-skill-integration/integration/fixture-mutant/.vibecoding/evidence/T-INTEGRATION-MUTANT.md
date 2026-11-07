<!-- generated-by: vb_gate v0.1.0 -->
# T-INTEGRATION-MUTANT 验证记录

Task: T-INTEGRATION-MUTANT
Time: 2026-11-08 01:08:05 +08:00
Baseline: 无版本基线（非 Git 仓库）
Environment: nt / Python 3.14.3 / cwd=<TEST_ROOT>\_release\host-evidence\integration-20261108-010759\fixture-mutant

| 验收 ID | 命令 / 步骤 | 退出码 | 结论 | 证据路径 | 限制 |
| --- | --- | --- | --- | --- | --- |
| AC-001 | `vb_trust 固定清单校验` | 0 | PASS | logs/T-INTEGRATION-MUTANT-AC001.log | == 可信校验: PASS（固定清单 v1.2.8；通过 37 / 失败 0 / 缺失 0 / 未登记 0）== |
| AC-002 | `"C:\Python314\python.exe" -I -B run_tests.py` | 1 | FAIL | logs/T-INTEGRATION-MUTANT-AC002.log | 仅本机环境 |

结论：FAIL
反向遗漏审查：待人工填写（本任务范围、确认的遗漏与处置）
审查：待人工填写（审查者、版本、结论）；本文件由 vb_gate v0.1.0 生成
Artifacts: logs/*.log
Recheck Conditions: 代码、依赖或测试变更后须重跑本门禁
Cleanup / Recovery: 日志保留于 evidence/logs/；无临时文件
Release Status: 未涉及

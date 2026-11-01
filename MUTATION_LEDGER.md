# 变异账本（R12，开发者自测，非 Reviewer 结论）

- 被测树：分支 fix/r11-closeout @ 2d85bdb（之后 8bf1030 只改非 Windows 平台的跳过逻辑，不影响 Windows 结果）
- 运行器：R11 Reviewer 的 r11_mutate.py 复制改造（假环境检查改为 vbdev_r12；新增 R12_* 变异）；每个变异跑全套 `python -B -m unittest discover -s tests`，Windows / Python 3.14，假 HOME/APPDATA/TEMP
- 合计 71：KILLED 59，SURVIVED 7（均已解释，无未解释缺口），N/A 5（均有改造替代）
- R11 账本 61 项对齐：52 KILLED 仍 KILLED；R11 两个缺口 M11/M20 现 KILLED；4 个等价/近等价仍存活并保留说明；3 个 N/A 仍以改造版 KILLED；新增 R12 变异 10 项 + R11_M13/M14 改 N/A

| 变异 | 结果 | 杀死它的测试（示例） | 说明 |
|---|---|---|---|
| R9_T1_no_unlisted_check | KILLED | test_argparse_pyc_via_flag, test_datetime_pyc_via_flag, test_extra_file_in_custom_standard |  |
| R9_T2_no_file_count | SURVIVED |  | 等价（R11 已判）：计数仅用于输出摘要，不影响判定 |
| R9_T3_exec_checked_dir_verify_manifest | KILLED | test_check_standard_failure_recorded_and_not_executed, test_extra_py_in_tools_is_unlisted, |  |
| R9_T4_no_pin_compare | KILLED | test_check_standard_failure_recorded_and_not_executed, test_self_consistent_tamper_with_re |  |
| R9_T5_missing_ignored | KILLED | test_t5_missing_vendor_file_refused |  |
| R9_T6_badhash_ignored | KILLED | test_r4n7_tampered_self_passing_vendor_refused_before_write, test_self_passing_custom_stan |  |
| R9_I1_load_trust_missing_allows | KILLED | test_i1_load_trust_missing_returns_none |  |
| R9_I2_src_precheck_removed | KILLED | test_r4n7_tampered_self_passing_vendor_refused_before_write, test_t5_missing_vendor_file_r |  |
| R9_I3_dest_recheck_always_true | KILLED | test_f6_interrupt_after_write_reports_written, test_i3_user_file_in_installed_vendor_fails |  |
| R9_I4_installer_KI_rc0 | N/A |  | N/A：模式在 HEAD 出现 2 次；改用 R9_I4a（KILLED） |
| R9_I5_load_trust_from_source | KILLED | test_R4N10_inner_junction_into_dest_refused, test_R4N10_manifest_invalid_keys_not_carried, |  |
| R9_J1_json_help_no_kind | KILLED | test_json_help_is_ok_and_marked_as_help |  |
| R9_J2_json_help_status_usage | KILLED | test_json_help_is_ok_and_marked_as_help |  |
| R9_K1_KI_status_ok | KILLED | test_interrupt_before_write_json_and_text, test_interrupt_during_write_json |  |
| R9_K2_KI_write_rc0 | KILLED | test_interrupt_during_write_json, test_interrupt_during_write_text |  |
| R9_K3_KI_no_rollback | KILLED | test_interrupt_during_write_json, test_interrupt_during_write_text |  |
| R9_K4_KI_prewrite_text_rc0 | N/A |  | N/A：模式已不存在；改用 R9_K4a（KILLED） |
| R9_K5_KI_claims_complete | KILLED | test_interrupt_during_write_text |  |
| R9_S1_skip_claims_verified | KILLED | test_skip_check_makes_no_signed_off_claim |  |
| R9_S2_skip_trust_pinned | KILLED | test_skip_check_makes_no_signed_off_claim |  |
| R9_S3_skip_summary_PASS | KILLED | test_skip_check_makes_no_signed_off_claim |  |
| R9_V1_init_verify_always0 | KILLED | test_extra_file_in_custom_standard_refused, test_self_consistent_tamper_with_regenerated_m |  |
| R9_G1_gate_checkstd_always0 | KILLED | test_check_standard_failure_recorded_and_not_executed, test_pyc_with_check_standard |  |
| R10_F1a_gate_trust_always0 | KILLED | test_argparse_pyc_via_flag, test_datetime_pyc_via_flag, test_pyc_via_env |  |
| R10_F1b_refused_struct_unknown | KILLED | test_argparse_pyc_via_flag, test_crafted_standard_via_flag_not_executed_and_not_pass, test |  |
| R10_F1c_refuse_only_rc2 | KILLED | test_argparse_pyc_via_flag, test_datetime_pyc_via_flag, test_pyc_via_env |  |
| R10_F1d_verify_vendored_exec_located | KILLED | test_argparse_pyc_via_flag, test_datetime_pyc_via_flag, test_pyc_via_env |  |
| R10_F1e_trust_ignores_extra_py | N/A |  | N/A：改用 R11_M1e（KILLED） |
| R10_F1f_trust_skips_tools_dir | KILLED | test_argparse_pyc_via_flag, test_datetime_pyc_via_flag, test_extra_py_in_tools_is_unlisted |  |
| R10_F1g_refuse_branch_still_runs | KILLED | test_argparse_pyc_via_flag, test_datetime_pyc_via_flag, test_pyc_via_env |  |
| R10_F2a_no_gitattributes | KILLED | test_gitattributes_lines |  |
| R10_F2b_vendor_not_binary | KILLED | test_gitattributes_lines |  |
| R10_F4a_recovery_no_force | KILLED | test_f4_recovery_after_interrupt_needs_force |  |
| R10_F5a_write_phase_not_set | KILLED | test_r9f5_interrupt_after_write_does_not_claim_nothing_written |  |
| R10_F5b_msg_always_prewrite | KILLED | test_r9f5_interrupt_after_write_does_not_claim_nothing_written |  |
| R10_F6a_outer_KI_rc0 | KILLED | test_f6_interrupt_after_write_reports_written, test_f6_interrupt_before_write_no_traceback |  |
| R10_F6b_written_not_recorded | KILLED | test_f6_interrupt_after_write_reports_written |  |
| R10_F6c_outer_KI_no_handler | KILLED |  |  |
| R10_F7a_load_trust_exc_stub | KILLED | test_i1_load_trust_missing_returns_none |  |
| R10_F7b_trust_count_ok_any | SURVIVED |  | 等价（R11 已判） |
| R9_I4a_inner_KI_rc0_adapted | KILLED | test_f4_recovery_after_interrupt_needs_force, test_interrupt_mid_install_reports_written_f |  |
| R9_K4a_prewrite_text_rc0_adapted | KILLED | test_interrupt_before_write_json_and_text, test_r9f5_interrupt_after_write_does_not_claim_ |  |
| R11_M1_trust_skip_pyc | KILLED | test_argparse_pyc_via_flag, test_datetime_pyc_via_flag, test_pyc_outside_pycache_is_unlist |  |
| R11_M1e_trust_skip_py_adapted_F1e | KILLED | test_extra_py_in_tools_is_unlisted, test_unregistered_file_in_vendor_refused |  |
| R11_M2_no_I | KILLED | test_pythonpath_ignored_by_isolated_mode, test_user_site_hooks_not_run_in_child |  |
| R11_M3_no_I_no_B | KILLED | test_pythonpath_ignored_by_isolated_mode, test_user_site_hooks_not_run_in_child |  |
| R11_M4_exec_located_with_I | KILLED | test_swap_after_read_verified_not_executed |  |
| R11_M4b_exec_located_noI_cwdstd | KILLED | test_located_dir_pyc_not_used_even_if_trust_bypassed, test_pythonpath_ignored_by_isolated_ |  |
| R11_M5_cwd_located_only | SURVIVED |  | 近等价（R11 已判）：-I 下 cwd 不进 sys.path，且执行的是私有副本 |
| R11_M6_rv_no_pin | KILLED | test_read_verified_requires_pinned_manifest |  |
| R11_M7_rv_no_hash | KILLED | test_read_verified, test_swap_after_verification_not_executed |  |
| R11_M8_write_reread_located | KILLED | test_swap_after_read_verified_not_executed |  |
| R11_M9_KI_unhandled | KILLED | test_keyboard_interrupt_diagnostic |  |
| R11_M10_KI_rc0 | KILLED | test_keyboard_interrupt_diagnostic |  |
| R11_M11_priv_not_removed | KILLED | test_private_dir_removed, test_private_dir_removed_when_child_crashes | R11 存活缺口 → R12 新测试杀死（R11-N2） |
| R11_M12_rv_none_struct_pass | KILLED | test_swap_after_verification_not_executed |  |
| R11_M13_guard_call_removed | N/A |  | N/A：R11-N5 重构后锚点不存在；由 R12_G1/G3/G4/G6 取代（均 KILLED） |
| R11_M14_guard_always_ok | N/A |  | N/A：同上，由 R12_G1 取代（KILLED） |
| R11_M19_priv_inside_located_tools | SURVIVED |  | 近等价（R11 已判）：私有副本字节已核对；目录位置不影响 -I 执行 |
| R11_M20_I_to_E | KILLED | test_user_site_hooks_not_run_in_child | R11 存活缺口 → R12 新测试杀死（R11-N2） |
| R11_M21_trust_check_skipped_for_explicit_standard | KILLED | test_argparse_pyc_via_flag, test_datetime_pyc_via_flag, test_pyc_via_relative_flag |  |
| R12_G1_guard_no_raise | KILLED | test_guard_checks_each_home_variable, test_guard_refuses_even_project_scope, test_guard_re |  |
| R12_G2_guard_ignores_HOME | KILLED | test_guard_checks_each_home_variable |  |
| R12_G2b_guard_ignores_USERPROFILE | SURVIVED |  | 等价：Windows 上 expanduser("~") 即取 USERPROFILE（已在检查列表中），POSIX 上安装器只用 HOME |
| R12_G3_install_bypasses_chokepoint | KILLED | test_R5N1_dest_itself_is_file, test_R5N1_parent_of_dest_is_file, test_f4_recovery_after_in |  |
| R12_G4_run_argv_bypasses_chokepoint | KILLED | test_R5N1_default_layout_dot_claude_is_file, test_guard_refuses_run_argv_entry, test_no_di |  |
| R12_G5_setup_no_fake_home | KILLED | test_R4N10_inner_junction_into_dest_refused, test_R4N10_manifest_invalid_keys_not_carried, |  |
| R12_G6_guard_checks_only_user_scope | KILLED | test_guard_checks_each_home_variable, test_guard_refuses_even_project_scope, test_guard_re |  |
| R12_N4_relative_evidence_unresolved | KILLED | test_bare_relative_file, test_relative_subdir_file |  |
| R12_N6_gate_test_vm_without_B | SURVIVED |  | 等价（纵深防御）：测试模块已设 PYTHONDONTWRITEBYTECODE=1 并被子进程继承 |
| R12_N6_cleanup_leak_silent | SURVIVED |  | 测试基础设施：残留断言只在真实泄漏时触发；修复后无泄漏，功能用例无法区分。由“全套运行后临时目录为空”的平台检查覆盖 |

# TODO（任务真相源）

> 本仓库由 Vibecoding-Standard@53eb391 的 `skill/` 子树拆出（见 `PROVENANCE.md`）。下文历史条目中的 `skill/...` 路径对应本仓库根目录。

状态取值：PASS（开发者自测）/ FAIL / UNKNOWN / NOT_RUN / OPEN。自测 PASS 不等于 R4 复核通过。

| ID | 事项 | 状态 | 说明 |
|---|---|---|---|
| INS-1 | install_skill.py `--force` 会 rmtree 删除未知内容 | 自测 PASS | 95d41bf；归属清单 + 冲突拒绝 + 链接/边界；待 R4 |
| CLI-1 | `--json` 失败路径输出契约 JSON（status/error/rc） | 自测 PASS | 60a4ed1 |
| CLI-2 | `--update-block` 状态与 rc 一致 | 自测 PASS | 原实现已正确，补测试；JSON 增加 status |
| CLI-3 | assets/AGENTS.block.md 与 BLOCK 渲染防漂移 | 自测 PASS | 原实现一致，补测试 |
| CLI-4 | vendor 定位与项目搬迁 | 自测 PASS | 原实现正确，补测试 |
| CLI-5 | 技能缺失如实报告 | 自测 PASS | 修复：显式 `--standard` 无效时原先静默回退到其他副本 |
| CLI-6 | init / 安装器幂等 | 自测 PASS | 补测试 |
| LNK-F | 文件级符号链接用例 | NOT_RUN | 本机无创建文件符号链接权限（需开发者模式/管理员）；目录 Junction 用例已运行 |
| R4-N1 | 安装器：普通文件占据所需目录位置，--force 下仍部分写入后 rc1 | 自测 PASS | a887cd9；预检判为冲突 rc2、零写入（含 --force）；待 R5 复核 |
| R4-N2 | vb_init `_compensate` 无归属判据，项目内 Junction 重定向导致误删 | 自测 PASS | 9c91a9e；仅当前内容==本进程写入值才还原/删除，否则记残留；新建目录登记 baseline 并在父路径校验；回滚跳过项一律进残留，不再宣称“已回滚” |
| R4-N3 | 安装器：内层链接分量 rc2（文档写 rc1） | 自测 PASS | a887cd9；平凡的退出码对齐：链接/越界 → REFUSED rc1；测试断言收紧为 rc==1 |
| R4-N4 | 安装器：dest 上层分量为 Junction 时跟随写出项目外 | 自测 PASS | 6a0d17a；project scope 下项目根（不含）→dest 各分量为链接 → REFUSED rc1；user scope 的 ~ 及其上层不检查（测试禁止触碰 ~，NOT_RUN） |
| R4-N5 | 安装器：未检查 dest 与 source 重叠 | 自测 PASS | 56c60fe；realpath 相同或互相包含 → REFUSED rc1，零写入 |
| R4-N6 | `--json` 包装层按字面匹配 argv | 自测 PASS（pt19u 授权） | d2a83c3+9429d47+cabbf7e；`--json --help` → status ok rc0 kind=help；KeyboardInterrupt → 回滚、INTERRUPTED rc130（JSON status=interrupted）；待 R9 |
| R4-N7 | `--standard` / VB_STANDARD_HOME 可指向任意自校验目录 | CLOSED（R11 复核；钉扎随后由 S-SKILL-01 / C-REL / OSS-1.2.9 升至 v1.2.9） | 92d56ec+3437fcf 起引入 vb_trust；曾钉 v1.2.7 / 候选 / v1.2.8 正式。**现行钉扎见下方 OSS-1.2.9**（v1.2.9 MIT，`46035ee2…`，38 文件） |
| R4-N8 | c08407d 残留报告描述不准确 | 自测 PASS | 691f4dc；补偿先 guard 后读，guard 失败不经被替换路径读取/描述，也不再宣称「本次未改动」 |
| R4-N9 | 项目位于盘符根目录时写入全被拒 | 自测 PASS | 608118c；`_inside` 根安全（根已以分隔符结尾时不再拼接），preflight 复用 |
| R4-N10 | 测试与清单的小缺口（清单中 ../、绝对路径键被保留等） | 自测 PASS + DOCS | ace30ec；合并时丢弃非法清单键；新增内层 Junction 指向 dest 内用例（杀 M2）。DOCS：清单无签名/认证，仅作归属记录，伪造匹配哈希可让文件被视为「本工具所有」 |
| R5-N1 | 安装器：dest 本身或其上层被普通文件占据时未进预检冲突（执行阶段异常 rc1，零写入） | 自测 PASS | 1900fd9；dest 及其不存在的上层位置被非目录占用 → 预检冲突 rc2，零写入（含 --force、默认 .claude 布局） |
| R5-N2 | R4-N2 核心机制缺测试保护 | 自测 PASS | a1a32c8；M4–M7 均 KILLED；待 R6 复核 |
| R5-N3 | 补偿阶段残留未在回滚后核对，描述可能与事实相反（R4-N8 延伸） | 自测 PASS（R8 修正） | 691f4dc 的撤销逻辑被 R7 判为回归（R7-N1）；368f20a：补偿时路径被重定向的残留不再撤销，只在回滚后更新描述（原路径已收敛、实际落点未知）；未被重定向的残留在回滚确认收敛后才撤销 |
| R5-N4 | 安装器 TOCTOU：预检后出现的占位文件 | DOCS | 「零写入」仅是预检层保证；预检与写入之间并发出现的占位仍可能导致执行阶段失败（rc1），不引入事务框架 |
| R5-N5 | HANDOFF §9 skip 计数不准 | 已更正 | skip 数随仓库所在盘而变：F: worktree 为 1，与 %TEMP% 同盘为 2 |
| R6-N1 | 开发者临时目录名与复核者冲突（vbr6/vbR6） | 已更正（流程） | R7 起开发专用目录 %TEMP%\vbdev_r7 |
| R6-N2 | M7 保护只有一个文本模式用例 | 自测 PASS | 337aef1；新增 --json 变体与「预先存在文件被他人改动」变体，M7 下两例均 FAIL |
| R7-N1 | 回滚按当前路径收敛撤销残留，掩盖经 Junction 写出项目外的覆盖（R5-N3 回归） | 自测 PASS | 368f20a；被重定向条目保留 ResidualRisk，不再输出「FAILED（已回滚」 |
| R7-N2 | R4-N4 检查用 startswith("..")，`..x` 分量可绕过 | 自测 PASS | fb53917；按首个路径分量判断是否越出项目 |
| R7-N3 | 文档过度承诺「任一层链接 → rc1」 | DOCS | 130753c；docstring 与 HANDOFF §3 写明不检查 user scope 的 ~ 上层、绝对/越出项目 --path 的上层 |
| R7-N4 | preflight 盘符根改动无测试保护（变异 E2 存活） | 自测 PASS | 41bb45e；只读调用 preflight(盘符根)，无越界误报；E2 KILLED |
| R7-N5 | 清单非法键只在重写清单时丢弃；Windows 别名键（NUL、尾点/空格、大小写）可通过过滤 | OPEN（Info） | 无变化时为丢键而重写清单会改变「无变化零写入」语义；别名键归属按源 rel 精确匹配，暂无实际影响 |
| R7-N6 | 项目外悬空 Junction 作上层被归为非目录占用 rc2 | 自测 PASS | 2289ccc；悬空链接按链接 REFUSED rc1，零写入 |
| R4-N6 余项 | `--json --help` status / KeyboardInterrupt | DEFERRED（待 Owner 决定） | R7 认为 status ok 在现有枚举内，但仍属行为契约选择，不改 |
| R4-c08407d | 对 c08407d（及本分支）的独立复核 | 已完成 R4 | R4-REPORT.md：PASS-with-findings；R5 复核 5327eb9..HEAD 待安排 |
| VENDOR-SCOPE | vendor 范围决策（全量 vendored 还是精简） | OPEN | 需 Chris 决定 |
| POC-PUSH | 私有仓 main / feat 推送 | CLOSED（2026-11-11） | `main` 与 `feat/standard-v1.2.8-migration` 已推至 `origin` @ `49be330`；正式公开 / tag / Release 仍需另批 |

## R9（独立仓库候选，开发者自测，非 Reviewer 结论）
| ID | 事项 | 状态 | 说明 |
|---|---|---|---|
| R9-0 | 拆仓（skill/ 子树为根，无历史）+ PROVENANCE | 自测 PASS | 64ec1d7、2550597 |
| R8-N1 | 非重定向残留回滚后核对测试 | 自测 PASS | 05fe9d4；杀变异 H |
| DOC-1 | 安装中途失败残留与恢复 | DOCS | 0479bad |
| VEN-1 | vendor 来源 | DOCS | 10cef5d；34/34 blob 与 53eb391 一致 |
| OSP-1 | 开源准备审计 | 仅发现，未处理 | b826d1f；L1–L3/P1–P5/D1–D2/V1–V3/I1–I2/A1，公开前需 Owner 决定 |
| R9-RES-1 | 中断回滚后可能残留空目录（快照只比文件） | OPEN | 已知残余 |
| R9-RES-2 | 安装器目标复检无判别测试（变异 I3 存活） | 自测 PASS（R10） | 更正：原“难以构造”不成立——R9 复核用“在已安装 vendor/templates/ 放用户文件后 --force”即可构造；R10 已加该用例，I3 KILLED |
## R10（R9 独立复核发现修复，开发者自测，非 Reviewer 结论）
| ID | 事项 | 状态 | 说明 |
|---|---|---|---|
| R9-F1 | vb_gate 执行未校验标准的 check_evidence.py | CLOSED（R11 复核；pyc 绕过经 R10-N1 修复） | 791ac43；先 vb_trust 固定清单校验，不过则不执行、结构校验 FAIL；--standard 与 VB_STANDARD_HOME 均覆盖 |
| R9-F2 | autocrlf=true 克隆导致 vendor 校验失败 | 自测 PASS | 9a96ac1；.gitattributes（eol=lf，vendor -text），renormalize 无 blob 变化 |
| R9-F3 | 文档/帮助与信任模型不一致 | DOCS | 7ce18bf |
| R9-F4 | 恢复说明“重跑同一命令”实际 rc2 | 自测 PASS | 00c0054；改为“加 --force 重跑”，测试固定 rc2/rc0 行为 |
| R9-F5 | 写入后中断仍称“未写入文件” | 自测 PASS | 1a2ef91 |
| R9-F6 | 写入循环外中断出 traceback | 自测 PASS | 00c0054；INTERRUPTED rc130，区分写入前/后 |
| R9-F7 | 未被杀死变异 I1/I3/T5/G1 | 自测 PASS | 791ac43、00c0054、0a0bc5b（0a0bc5b 只改测试） |
| R9-F9 | Actions 描述不实 | DOCS | 见 HANDOFF R10 段；未改仓库设置 |
| R10-RES-1 | vb_trust 校验与执行 check_evidence 之间存在 TOCTOU 窗口 | CLOSED（被 R10-N2 取代：一次读入核对、执行私有副本） | 剩余私有目录竞态见 R11-RES-1 |
| R10-RES-2 | vb_trust 忽略 __pycache__/*.pyc（R9-F8） | 更正：R10 复核实测可利用（R10-N1 High），R11 处理 | 原“理论可能/info”判断错误 |
## R11（R10 复核发现修复，开发者自测，非 Reviewer 结论）
| ID | 事项 | 状态 | 说明 |
|---|---|---|---|
| R10-N1 | 外部标准目录无源 .pyc 被 check_evidence.py 导入，伪造 PASS | 自测 PASS | 070bf45；vb_trust 把 __pycache__ 外的 .pyc/.pyo 记为未登记；vb_gate 只执行写入私有临时目录的已核对字节，`-I -B` |
| R10-N2 | 校验与执行之间 TOCTOU | 自测 PASS | 070bf45；`vb_trust.read_verified` 一次读入并核对，执行内存字节的私有副本；mock 替换测试 |
| R10-N3 | 文档/帮助/TODO 措辞 | DOCS | 本段提交 |
| R10-N4 | vb_gate 中断 traceback | 自测 PASS | 070bf45；INTERRUPTED rc130 |
| R10-N5 | F1b/F1f/F2a/F2b 变异存活 | 自测 PASS | 070bf45 |
| R10-N6 | HANDOFF 0a0bc5b 描述 | DOCS | 已更正：0a0bc5b 只改测试 |
| R11-G | user scope 测试真实 HOME 防护 | 自测 PASS | 1beb807；HOME 不在测试临时目录内即硬失败、不运行安装器 |
| R11-RES-1 | 私有临时目录在执行期间可被同一用户进程改写 | OPEN | 同用户攻击者不在威胁模型内；另：未含 gh-118486 修复的 Python（<3.12.4、<3.11.10、<3.10.15）在 Windows 上 mkdtemp 不设限制性 ACL（继承 %TEMP% ACL），且 %TEMP% 可能授予其他主体（如 CodexSandboxUsers）修改权限，此时其他主体也可能在窗口内改写，见 SECURITY.md |
| R11-RES-2 | `__pycache__/` 内文件仍被 vb_trust 容忍 | OPEN（设计决定） | 不被执行：vb_gate 不从标准目录导入；vb_trust PASS 不代表可在原地安全运行标准自带脚本（SECURITY.md） |
| R11-RES-3 | --python 指定的解释器由调用者信任 | OPEN（设计边界） | R12 补齐：`vb_gate.py --help`、04-evidence-gate.md、SECURITY.md |
## R12（R11 复核收尾，开发者自测，非 Reviewer 结论；分支 fix/r11-closeout）
| ID | 事项 | 状态 | 说明 |
|---|---|---|---|
| R11-N1 | 用户文档默认校验命令 | 自测 PASS | README/VENDOR-PROVENANCE 只给 vb_trust；verify_manifest 仅为 Standard 自检、非信任根 |
| R11-N2 | M20（-I→-E）、M11（私有目录不删）存活 | 自测 PASS | 用户 site usercustomize/.pth（假 APPDATA）不得在子进程执行；正常/子进程失败两种情况均无 vb_gate_std_* 残留 |
| R11-N3 | 文档：--python 边界、RES-1 ACL 说明、错别字、状态一致 | DOCS | 本段 + SECURITY.md |
| R11-N4 | 相对 --evidence 回溯/结构校验 FAIL | 自测 PASS | 按 cwd 解析为绝对路径；ev.md 与 sub/ev.md 测试 |
| R11-N5 | 真实 HOME 防护可绕过 | 自测 PASS | 所有安装器调用经唯一入口 run_installer；默认假 HOME；--scope=user、run_argv、仅 HOME/仅 USERPROFILE 越界均拒绝；元测试禁止直接调用 |
| R11-N6 | 测试生成 __pycache__ / 临时目录残留 | 自测 PASS | verify_manifest 以 -B 运行；测试禁写字节码；git 只读对象强制删除，残留即报错 |

## S-SKILL-01 / 私有基线（main @ 1378828+；Owner 签收 2026-11-11）
| ID | 事项 | 状态 | 说明 |
|---|---|---|---|
| S-SKILL-01 | vendor 迁至 Standard v1.2.8 工程候选 `2e010b0`；关闭 R15-N4 A/B/C | 自测 PASS；已合 main；后由 C-REL 升正式 | 候选期钉 `ac261bc2…`；现由 C-REL 取代 |
| OWN-1 | 受管块归属：仅可信渲染可 `--update-block`；config path 不参与信任 | 自测 PASS | `e089fe0`、`0a84036` |
| IR-1 | 合入前独立复核：legacy 夹具 NEW→OLD 污染含版本号路径 | CLOSED | 假红；`49be330` 改为冻结模板×解算 vref + `split_block`/EOL + 断言；回归钉 `test_s02c` |
| IR-2 | 合入前独立复核：CRLF 下块替换静默失败 | CLOSED | 同 `49be330` |
| BASELINE | 私有工程基线冻结（非正式 Release） | CLOSED（Owner 签收 2026-11-11） | 签收 tip 文档基线 `1378828`（含夹具修复 `49be330`）。后由 C-REL 升至 Standard 私有正式身份 |
| C-REL | 阶段 C：Standard v1.2.8 私有正式发版 → Skill 钉扎 | 自测 PASS | Standard `v1.2.8` @ `d9abf27`；后由 OSS-1.2.9 取代为公开 MIT 钉扎 |
| OSS-1.2.9 | Owner 确认 MIT/YunAbove/2026；Standard v1.2.9 + Skill 钉扎 + 两仓 Public | 自测 PASS | Standard tip `b1ece9f` / tag `v1.2.9`；Skill vendor 钉 `46035ee2…`；LICENSE 生效；unittest 217 OK skipped=2；公开见 `gh repo edit` |
| OSP-1 | 开源准备审计 | CLOSED（L1/L2 解除） | Owner 确认后 MIT 授予；见 `LICENSE` / vendor `LICENSE`；公开后仍 OPEN：VENDOR-SCOPE、R11-RES-*、R9-RES-1、LNK-F、I1 |


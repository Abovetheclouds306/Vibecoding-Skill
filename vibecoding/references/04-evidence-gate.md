# 04 · 证据门禁与退出码

## 三态契约

| 码 | 含义 | 触发条件（任一） |
| --- | --- | --- |
| `0` | PASS | 全部验证已运行、退出码均 `0`、证据字段完整 |
| `1` | FAIL | 任一验证退出码非 `0`；或证据中可靠解析出确定失败 |
| `2` | UNKNOWN | 有验证未运行；证据字段缺失/不可解析；需人工决定；省略必要参数 |

**严重度 `1 > 2 > 0`**：有确定失败时不因同时存在不确定项而降级为 `2`。

**`2` 的两个禁止**：不得当通过，也不得当"跳过"。`if rc == 2: skip` 是典型绕过写法。

## 生成证据（推荐）

```bash
python scripts/vb_gate.py --project <项目> --task T-001 \
  --verify "python -m unittest discover -s tests -v" \
  --verify "python -m compileall -q src" \
  --task-status REVIEW
```

行为：

1. 逐条执行 `--verify`，记录命令、实际退出码、输出尾部、耗时。
2. 写 `.vibecoding/evidence/T-001.md`（字段对齐标准模板）。
3. 先用技能自带 `scripts/vb_trust.py`（固定 v1.2.8 清单 SHA-256）核对标准副本（`__pycache__` 之外的 `.pyc` 等未登记文件一律 FAIL）；通过后只把已核对的 check_evidence.py 字节复制到私有临时目录，以 `python -I -B` 运行做结构校验（不在被定位目录执行或导入任何文件，校验与执行之间无替换窗口），把它的退出码并入汇总。核对不通过时**不执行**该脚本，结构校验记 FAIL（`--standard` / `VB_STANDARD_HOME` 只改变读取位置，不改变信任判据）。
4. 打印结论横幅并以其为进程退出码。

信任边界（详见仓库根 `SECURITY.md`）：

- `--python` 指定的解释器由**调用者信任**：本工具不校验解释器本身，它可以伪造任何结果。
- `--verify` 运行的是你自己写的命令，同样由调用者信任；门禁只记录其退出码。
- `--evidence` 相对路径按当前工作目录解析为绝对路径。
- 私有临时目录由 `tempfile.mkdtemp` 创建；能以同一用户身份运行代码的攻击者不在威胁模型内（见 SECURITY.md 的临时目录权限说明）。

**没有 `--verify` 时**：默认 `NOT_RUN` → 退出码 `2`，横幅为 `UNKNOWN`。要写作"本任务无自动验证"，必须显式 `--allow-missing-verify`，此时仍会在证据里标注"无自动验证"。

## 证据文件必备字段

由 `check_evidence.py` 强制（缺字段 → `UNKNOWN`，不是 PASS）：

- 头部：`Task:`、`Time:`（**日期 + 具体时刻 + 时区**，三者缺一即 UNKNOWN）、`Baseline:`、`Environment:`
- 验收表：`验收 ID | 命令/步骤 | 退出码 | 结论 | 证据路径 | 限制`
- `结论：` 总结论
- `反向遗漏审查：`、`Artifacts:`、`Recheck Conditions:`、`Cleanup / Recovery:`、`Release Status:`

## 常见假 PASS（本技能要防的就是这些）

| 场景 | 旧行为的后果 | 现在的判定 |
| --- | --- | --- |
| 验收行写 `NOT_RUN` 且原因有效 | 曾判 PASS | 非 DONE → `UNKNOWN`；DONE → `FAIL` |
| 全部验收行 `FAIL` 但没写总结论 | 曾判 PASS | `FAIL` |
| 省略 `--task-status` | 曾判 PASS | `UNKNOWN`（声明未做 DONE 完整性检查） |
| 有两个验收表，第二个全 FAIL | 曾静默忽略 | `UNKNOWN`（不做跨表聚合） |
| 表头漏写分隔行 | 曾吞表头后判 PASS | `UNKNOWN` + 行号 |
| 测试设计清单（`用例 ID｜预期结果`） | 曾被误判为验收表 | 不参与验收判定 |
| 上面这些之外 | — | 边界固定三档，不为无限 Markdown 变体扩解析器 |

## 人工检查怎么写

```markdown
| AC-003 | 人工核对导出文件表头 | N/A | PASS | evidence/export-header.png | 仅 Windows |
```

`N/A` 退出码**只允许**用于明确标注的人工检查，且必须给可定位证据与原因。自动化命令写 `N/A` 会被判不确定。

## 与 CI 的关系

`vb_gate.py` 是普通 Python 脚本，可直接进 CI 当作一个 step：

```yaml
- run: python <skill>/scripts/vb_gate.py --task "$TASK" --verify "pytest -q" --task-status DONE
```

退出码非 0 即使 CI 失败——**这是本技能唯一"不依赖模型自觉"的保障层**。

## 自检口诀

> 结论前面必须有"我跑过什么、它返回几"。没有退出码的 PASS 一律视为 `NOT_RUN`。

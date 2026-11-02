# vendor/vibecoding-standard 只读副本

## 这是什么

Vibecoding Standard **v1.2.8** 签收内容的**逐字节副本**，随本技能分发，使技能在离线、无标准仓库的机器上仍可执行门禁与查阅规则原文。

## 来源与身份

| 项 | 值 |
| --- | --- |
| 标准版本 | 1.2.8 |
| 签收提交 | `2e010b04059172b651c191bf1dbaab279c8d78be` |
| 签收 Tree | `1e6c4e65f148353c851318a43cb98846250e8823` |
| 发布提交（merge） | PENDING |
| Tag | PENDING |
| 来源 | `git archive 2e010b0`（Standard 本地仓库导出；无发布包） |
| 来源包 SHA-256 | PENDING（不以本地构建 ZIP 冒充） |
| 文件数 | 38（37 个登记文件 ＋ `MANIFEST.sha256`） |
| 落地方式 | 解出 `git archive` 归档到本目录，路径与文件名不变（Python tarfile，保留 UTF-8 文件名） |

## 校验（任何改动疑虑都先跑它）

```bash
python vendor/vibecoding-standard/tools/verify_manifest.py
# 期望：通过 37 / 失败 0 / 缺失 0 / 未登记 0 -> 清单校验: PASS
```

S-SKILL-01 实测（2026-11-02）：`vb_trust` PASS 37；与签收树 `2e010b0` 38 个 blob **逐一 SHA-1 相等**（缺失 0 / 不一致 0 / 多余 0），见 `VENDOR-PROVENANCE.md`。

## 纪律

1. **禁止在此目录内编辑任何文件**。规则有问题 → 回标准仓库走变更流程 → 发新版本 → 整体替换本目录。
2. 升级方式：替换整个目录 → 跑上面的校验 → 更新 `SKILL.md` frontmatter 的 `metadata.standard_version` 与 `standard_vendored_sha256`，并同步 `scripts/vb_trust.py` 的 `PINNED_MANIFEST_SHA256` / `PINNED_FILE_COUNT`。
3. 本目录**不是**第二份可独立维护的母规范；它没有独立版本号，只跟随标准版本。
4. 若校验失败：本技能的初始化与门禁都会拒绝执行（`vb_init.py` 直接退出码 1），以免用漂移的规则做判定。
5. 可信判据（R4-N7）：`scripts/vb_trust.py` 固定 `MANIFEST.sha256` 的 SHA-256 并逐文件核对，vb_init / vb_gate / 安装器都用它；上面的 verify_manifest.py 只证明自洽。完整来源与 blob 对照见独立仓库根目录 `VENDOR-PROVENANCE.md`。
6. 上表“来源包 SHA-256”指发布 ZIP 文件哈希（SKILL.md 中 `standard_vendored_sha256` 同值）；v1.2.8 尚未发布，两处均为 PENDING。

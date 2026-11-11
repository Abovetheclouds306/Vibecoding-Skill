# vendor/vibecoding-standard 只读副本

## 这是什么

Vibecoding Standard **v1.2.8** 私有正式发布内容的**逐字节副本**，随本技能分发，使技能在离线、无标准仓库的机器上仍可执行门禁与查阅规则原文。

## 来源与身份

| 项 | 值 |
| --- | --- |
| 标准版本 | 1.2.8 |
| 签收提交（工程候选） | `2e010b04059172b651c191bf1dbaab279c8d78be` |
| 发布提交 | `d9abf273ff3ee7afebf39541c7a031922e1bb5be` |
| 发布 Tree | `d21d9d1dfef7bffb2e672aea57b2da0bf09d1899` |
| Tag | `v1.2.8` |
| 来源 | `git archive d9abf27`（与私有正式 ZIP 同源） |
| 来源包 SHA-256 | `6f3ca956f942e219bbc3dca62ca58e570a701ffee8a1726721483f9993aa54df` |
| 文件数 | 38（37 个登记文件 ＋ `MANIFEST.sha256`） |
| 落地方式 | 解出 `git archive` 归档到本目录，路径与文件名不变（Python tarfile，保留 UTF-8 文件名） |
| 许可 | 仍为私有 / `LICENSE-DRAFT`（**未**开源授权） |

## 校验（任何改动疑虑都先跑它）

```bash
python ../scripts/vb_trust.py .
# 期望：== 可信校验: PASS（固定清单 v1.2.8；通过 37 / 失败 0 / 缺失 0 / 未登记 0）==
```

`tools/verify_manifest.py` 只证明自洽，**不是**信任根；勿在已安装目录就地运行（会写 `__pycache__`）。

## 纪律

1. **禁止在此目录内编辑任何文件**。规则有问题 → 回标准仓库走变更流程 → 发新版本 → 整体替换本目录。
2. 升级方式：替换整个目录 → 跑 `vb_trust` → 更新 `SKILL.md` frontmatter 与 `scripts/vb_trust.py` 的 `PINNED_*` / 发布身份常量。
3. 本目录**不是**第二份可独立维护的母规范；它没有独立版本号，只跟随标准版本。
4. 若校验失败：本技能的初始化与门禁都会拒绝执行，以免用漂移的规则做判定。
5. 可信判据：`scripts/vb_trust.py` 固定 `MANIFEST.sha256` 的 SHA-256 并逐文件核对。完整来源见仓库根 `VENDOR-PROVENANCE.md`。

# 上架指南（CONTRIBUTING）

把插件放进 EasyPlugin 商店只需要三步：**发布 Release → 算哈希 → 提 PR**。

## 一、发布前检查

作者仓库根目录应当有：

| 文件 | 要求 |
|---|---|
| `manifest.json` | 至少含 `name` 与 `kind`（`plugin` 或 `theme`）；`name` 必须是合法 Python 标识符，且与源码里的顶层类名一致 |
| 源码 | 插件为 `<name>.py`；主题为 `<name>.def`（含同名节） |
| `README.md` | 说明用途与用法 |
| `LICENSE` | 明确开源许可 |

另外强烈建议在仓库设置里开启 **Immutable Releases**
（Settings → General → Releases），开启后已发布的附件不可增删改、tag 不可移动，
并能用 `gh release verify-asset` 独立核验。开启后发 Release 需走「先建 draft → 传附件 → 再发布」。

## 二、发布 Release

1. 把 `manifest.json` 里的 `version` 写成语义化版本（`主.次.修订`）；
2. 打 tag `v<version>`（tag 与 `version` 必须一致）；
3. 新建 Release，上传一个 ZIP 附件，命名 `<id>-<version>.zip`。

ZIP 包内部结构（与客户端本地导入格式完全一致）：

- `manifest.json`：名称、类型、版本、作者、许可、简介、enable；
- 内容文件：插件为 `<name>.py`，主题为 `<name>.def`。

## 三、算 sha256

```bash
# Linux / macOS
sha256sum <附件名>

# Windows PowerShell
Get-FileHash .\<附件名> -Algorithm SHA256

# Windows CMD
certutil -hashfile <附件名> SHA256
```

结果必须是小写、64 位十六进制。

## 四、提 PR

Fork 本仓库，编辑 `index.json`，在 `packages` 数组里**按 `id` 字母序**插入一条。
字段一览：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `id` | 字符串 | 是 | 唯一标识；插件必须是合法 Python 标识符，与类名一致 |
| `kind` | 字符串 | 是 | `plugin` 或 `theme` |
| `name` | 字符串 | 是 | 显示名 |
| `version` | 字符串 | 是 | 语义化版本，须与 Release tag 一致 |
| `author` | 字符串 | 是 | 作者名 |
| `license` | 字符串 | 否 | 开源许可 |
| `summary` | 字符串 | 是 | 一句话简介，卡片直接显示，不要换行，上限 120 字 |
| `repo` | 字符串 | 是 | 作者仓库，形如 `owner/name` |
| `asset` | 字符串 | 是 | Release 附件名，以 `.zip` 结尾 |
| `sha256` | 字符串 | 是 | 附件的小写 sha256 |
| `min_client` | 字符串 | 否 | 要求的最低客户端版本，形如 `1.0` |
| `yanked` | 布尔 | 否 | 下架标记，由维护者操作 |
| `yank_reason` | 字符串 | 否 | 下架原因，`yanked` 为 `true` 时必填 |

除了 `index.json`，**不要改动本仓库的其他文件**（改动策略文件请另开 PR 说明理由）。

提交前先本地跑一遍：

```bash
python scripts/validate_index.py
```

然后提 PR，标题写 `Add plugin: <id>`，按 PR 描述里的清单逐项勾选。

## 五、常见驳回原因

| 现象 | 原因 |
|---|---|
| CI 报 `sha256 长度不对` | 粘成了大写，或只复制了前几位 |
| CI 报 `未按 id 字母序排列` | 直接追加到了数组末尾 |
| CI 报 `id 不是合法 Python 标识符` | 插件名带了 `-` 或空格 |
| CI 报 `version 与 tag 不一致` | `manifest.json` 写 `1.0`、tag 打 `v1.0.0` |
| 驳回 | 声明与实际行为不符、代码有网络请求或执行外部命令、README 缺失 |
| 驳回 | 功能与已有条目重复 |

## 六、更新已上架插件

1. 作者仓库里升 `manifest.json` 的 `version`，发新 Release（新 tag、新附件）；
2. 在本仓库提 PR，把该条目的 `version` / `asset` / `sha256` 一起改掉；
3. **同一个版本号的附件内容不许变**——内容变了必须升版本，这是硬规则。

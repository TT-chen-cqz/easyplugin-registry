# EasyPlugin Registry

这是 EasyPlugin 的**控制仓库**：里面**只有索引与治理文件，没有插件代码**。
插件源码放在作者自己的仓库，发布走 GitHub Release 附件。

## 目录结构

```
easyplugin-registry/
├── index.json                      索引：全部条目（客户端读这个）
├── schema/index.schema.json        索引的 JSON Schema
├── scripts/
│   ├── validate_index.py           离线校验（CI 与本地共用，纯标准库）
│   └── verify_release.py           联网核对：下载附件重算 sha256（维护者用）
├── .github/
│   ├── workflows/validate.yml      PR 校验
│   ├── workflows/publish.yml       合并后发布到 store 分支
│   ├── workflows/verify-release.yml 手动触发的附件核验
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── CODEOWNERS
├── CONTRIBUTING.md                 上架流程（作者看这个）
└── POLICY.md                       索引规则与下架规则（维护者看这个）
```

## 分支约定

| 分支 | 用途 | 谁能写 |
|---|---|---|
| `main` | 源文件与改动记录，改动一律走 PR | 维护者 |
| `store` | 由 `publish.yml` 自动同步的发布副本，**客户端只读这个** | 机器人 |

客户端只信任 `store` 分支：即使 `main` 被人误改，发布内容也只在合并后才更新。

## 客户端接入

### 1. 官方源（默认）

```
https://raw.githubusercontent.com/TT-chen-cqz/easyplugin-registry/store/index.json
```

国内直连 GitHub 可能不通，客户端应支持把 `https://raw.githubusercontent.com/`
替换为镜像前缀（例如反向代理域名），并缓存上一次成功拉取的索引供离线使用。
附件下载地址（`https://github.com/`）同样应支持镜像前缀，两个前缀分别配置。

### 2. 自定义控制仓库

EasyPlugin 允许用户添加任意**格式相同**的控制仓库（私有小圈子、公司内网镜像都行）。
客户端行为约定：

- 每个源在界面上单独标注来源（取索引里的 `registry` 字段）；
- 多个源的条目按 `id` 合并，**同 id 冲突时官方源优先**，并提示用户；
- 自定义源拉取失败只影响该源，不影响官方源。

### 3. 下载地址约定

客户端按「仓库 + 版本 + 附件名」拼固定地址，**不用 `latest`**：

```
https://github.com/<repo>/releases/download/v<version>/<asset>
```

这样索引里的 `sha256` 与下载内容一一对应，作者事后换附件也装不上。

## 作者上架三步

1. 在自己的插件仓库里准备好 `manifest.json` 与源码，打 tag `v1.0.0`，
   建 GitHub Release 并把 `<id>-<version>.zip` 作为**附件**上传
   （ZIP 结构见 CONTRIBUTING.md）。
2. 算出附件的 sha256。
3. Fork 本仓库，在 `index.json` 里**按 `id` 字母序**插入一条，提 PR。

详细步骤与常见驳回原因见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 本地自检

```bash
python scripts/validate_index.py
```

校验不过会列出具体第几条、哪个字段有问题。

## 相关文档

- [CONTRIBUTING.md](CONTRIBUTING.md)：上架流程
- [POLICY.md](POLICY.md)：索引规则、安全要求、下架规则

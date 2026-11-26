# 小小城镇（简体中文版）

基于 Derek Yao 的 [Little City](https://github.com/yaoderek/littlecity.io) 发布包制作的独立汉化工程。默认简体中文，不提供英文切换。保留原游戏的程序逻辑、3D 素材和存档格式。

`main` 提供原版简体中文构建。`jiangnan` 用于江南风格开发，继承 `v6` 的场景与建筑改动。历史版本可通过 `v1` 至 `v6` 和 `v5-audit` 标签检出。

## 构建

固定上游版本：`af6eac24ff21cbf027d4d33fd8219237a559f5b5`（对应上传的 gh-pages ZIP）。

```bash
python -m pip install -r requirements.txt
python build.py
```

或者使用已有 ZIP 离线构建（依赖已安装）：

```bash
python build.py --source littlecity.io-gh-pages.zip
```

输出：`dist/`，可直接静态托管。无需运行 Node 后端、数据库或游戏服务器。Node 可用时自动执行 JavaScript 语法检查。构建时生成 `localization-report.json`，记录未匹配静态文本供进一步复核。

## Cloudflare Pages

- 连接仓库：`yuxingyizhou/demo`
- 生产分支：`main`
- 框架预设：None
- 构建命令：`python -m pip install -r requirements.txt && python build.py`
- 输出目录：`dist`
- 根目录：留空
- 环境变量：可选 `SITE_URL=https://你的实际域名`

## 汉化范围

- 主界面、建筑工具、时间、季节、天气、存档、菜单、图鉴与提示。
- 全部 102 个图鉴条目的名称、建造条件和活动说明。
- 关于页、图鉴索引、404、分享卡片、网页标题与安装清单。
- 禁用上游 PostHog 初始化；不改动游戏机制和用户自定义存档名称。

已构建 108 个页面，并在桌面 Chromium 上验证语言、分享标题、WebGL 2、岛屿及生成菜单和自定义存档名称。移动端触控布局及低频动态事件仍待完整验收。

## 权利说明

原项目作者为 Derek Yao；原始代码、素材、音乐等权利归原权利人。本仓库仅保存汉化工程与构建脚本，并非上游项目授权的声明。本仓库的 LICENSE 不代表上游素材获得同样授权。未经权利人许可，不应公开发布原项目的衍生作品。若部署用于个人验证，应通过访问控制限制访问；noindex 不是访问控制。

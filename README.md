# 📺 IPTV Auto-Update & Sort (Qinglong Edition)

本项目是一个基于 **青龙面板 (Qinglong)** 的 IPTV 直播源自动整理工具。通过多源聚合、深度嗅探测速以及智能排序，旨在为用户提供一个稳定、整洁且秒开的私人直播列表。

[Image of an automated workflow diagram showing data fetching from multiple M3U sources, processing via a Python script in a Docker container, and pushing to a GitHub repository]

---

## ✨ 核心功能

* **🔗 动态订阅**：通过环境变量 `IPTV_SOURCES` 集中管理来源，无需频繁修改代码。
* **🚀 央视置顶**：自动识别 CCTV 频道并置顶，按 1-17 自然数字顺序排列，修正 CCTV-10 乱序问题。
* **🔍 深度嗅探**：不仅检查 HTTP 状态码，还会尝试读取 512 字节视频数据，确保链接“真实可播放”。
* **🌐 IP 版本控制**：支持通过变量一键切换 **纯 IPv4**、**纯 IPv6** 或 **双栈保留** 模式。
* **🛡️ 运营商源保护**：自动识别移动/联通等运营商单播、酒店源，针对特定环境强制保留，防止误删。
* **🔄 自动同步**：脚本内置 Git 初始化与强制推送逻辑，自动更新至指定的 GitHub 仓库。

---

## 🛠️ 环境依赖与变量配置

### 1. 软件依赖
* **青龙面板** (Docker 环境)
* **Python3 依赖**：`requests` (在青龙面板“依赖管理”中安装)
* **Linux 依赖**：`git` (通常青龙自带，若无请在依赖管理安装)

### 2. 环境变量设置
请在青龙面板的 **环境变量** 页面添加以下变量：

| 变量名称 | 是否必填 | 说明 | 示例值 |
| :--- | :--- | :--- | :--- |
| `IPTV_SOURCES` | **是** | 订阅源列表，每行一个 URL | `https://url1.m3u` <br> `https://url2.m3u` |
| `GITHUB_TOKEN` | **是** | 具有 repo 权限的 GitHub Token | `ghp_xxxxxxxxxxxx` |
| `GITHUB_USER` | **是** | 你的 GitHub 用户名 | `yourname` |
| `GITHUB_REPO` | **是** | 存储 M3U 的仓库名 | `iptv-list` |
| `IP_VERSION` | 否 | 筛选 IP 版本: `4`, `6` 或 `all` | `4` (默认为 all) |
| `GITHUB_EMAIL` | 否 | Git 提交记录用的邮箱 | `bot@mail.com` |

---

## 🛰️ 订阅方式

任务运行成功后，你可以在电视盒子（TiviMate, OTT Navigator）或电脑播放器（PotPlayer）中填入你的 **GitHub Raw** 链接：

`https://raw.githubusercontent.com/你的用户名/你的仓库名/main/iptv_tested_final.m3u`

---

## ❓ 常见问题排查 (FAQ)

1. **为什么生成的有效源很少？**
   - **网络隔离**：GitHub 的源多为内网源，海外服务器或无 IPv6 环境会剔除无法连通的源。
   - **OpenClash 干扰**：脚本已内置绕过代理逻辑，但仍建议 OpenClash 使用 Fake-IP 模式并检查访问控制。

2. **推送报错 `fatal: not a git repository`？**
   - 脚本已包含自动初始化。若仍报错，请检查 `GITHUB_USER` 和 `GITHUB_REPO` 环境变量填写是否准确。

---

## ⚖️ 免责声明

1. 本脚本仅用于技术研究及学习，请勿用于商业用途。
2. 脚本抓取的直播源均来自互联网公开仓库，本项目不存储、不分发任何音视频资源。
3. 用户使用本工具应遵守当地法律法规，版权纠纷由使用者自行承担。
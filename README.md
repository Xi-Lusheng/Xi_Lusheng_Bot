# <center>汐鹿生Bot</center>

---

## 关于项目

**此项目基于 Python [Nonebot2](https://v2.nonebot.dev/) 开发 Q 群机器人**

协议端已从陈旧的 `go-cqhttp` 迁移到 **OneBot V11** 适配器，可对接目前仍在维护的客户端：

* [NapCat](https://github.com/NapNeko/NapCatQQ)（推荐）
* [Lagrange.OneBot](https://github.com/LagrangeDev/Lagrange.Core)
* [LLOneBot](https://github.com/LLOneBot/LLOneBot)

---

### 前言

此项目仅用于学习交流，请勿用于非法用途

---

## 环境要求

* **Python >= 3.9**（当前虚拟环境为 Python 3.14，已验证可用）
* 一个 OneBot V11 协议端（NapCat / Lagrange.OneBot / LLOneBot 任选其一）
* 可选：[ffmpeg](https://ffmpeg.org/)（发送语音用），配置到环境变量

---

## 运行项目

### 1. 安装依赖

本项目自带虚拟环境目录 `.Nonebot`，可直接使用：

```
.Nonebot\Scripts\python.exe -m pip install -r requirements.txt
```

或者自己建一个虚拟环境：

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

依赖清单见 [requirements.txt](requirements.txt)：

| 依赖 | 用途 |
| --- | --- |
| `nonebot2` | 框架本体（>= 2.4.4） |
| `nonebot-adapter-onebot` | OneBot V11 适配器 |
| `nonebot-adapter-console` | 本地无客户端时的调试控制台（默认不启用） |
| `Pillow` / `numpy` | pixiv 插件的「幻影坦克」图片合成 |
| `httpx` / `requests` | 请求外部 API |
| `nb-cli` | 命令行工具（`nb run` 等） |

> `playwright` 是**可选**依赖，只影响 `destiny2` 插件的「日报」功能。
> 未安装时该功能会提示不可用，不会影响其它插件。

### 2. 修改配置

机器人配置放在 `.env.prod`（生产）和 `.env.dev`（开发），
由 [.env](.env) 里的 `ENVIRONMENT` 决定加载哪一个：

```
ENVIRONMENT=prod   # 加载 .env.prod
ENVIRONMENT=dev    # 加载 .env.dev
```

常用配置项：

```
# 配置 NoneBot 超级用户
SUPERUSERS=["12345678"]

# 配置主人名称
MASTER=["汐鹿生"]

# 配置机器人的昵称
NICKNAME=["初号姬"]

# 配置命令起始字符
COMMAND_START=["/"]

# 配置命令分割字符
COMMAND_SEP=["."]

# 默认不启用控制台 TUI 适配器，需要本地调试时改为 true
ENABLE_CONSOLE_ADAPTER=false
```

详细配置请阅读 [nonebot2](https://v2.nonebot.dev/) 官方文档。

### 3. 启动机器人

```
nb run
# 或
.Nonebot\Scripts\python.exe bot.py
```

启动成功后会看到：

```
[SUCCESS] nonebot | Loaded adapters: OneBot V11
[SUCCESS] nonebot | Running NoneBot...
[INFO] uvicorn | Uvicorn running on http://127.0.0.1:9090
```

### 4. 让协议端连接上来

NoneBot 和协议端之间有两种连接方式，**任选一种，不要同时开**。

#### 方式一：反向 WebSocket（推荐）

协议端主动连到 NoneBot，NoneBot 当服务端。用默认驱动器即可，**不需要改任何配置**。

在协议端里把「反向 WebSocket / WebSocket 客户端」地址填成：

```
ws://127.0.0.1:9090/onebot/v11/ws
```

各协议端的具体位置：

<details><summary>NapCat</summary>

启动 NapCat，控制台会打印 WebUI 地址和默认 token；用浏览器打开 WebUI，
进入 **网络配置** → **新建** → **WebSocket 客户端**，
URL 填 `ws://127.0.0.1:9090/onebot/v11/ws`，保存并启用。

</details>

<details><summary>Lagrange.OneBot</summary>

修改 `appsettings.json` 的 `Implementations`，加入一项：

```json
{
  "Type": "ReverseWebSocket",
  "Host": "127.0.0.1",
  "Port": 9090,
  "Suffix": "/onebot/v11/ws",
  "ReconnectInterval": 5000,
  "HeartBeatInterval": 5000,
  "AccessToken": ""
}
```

</details>

<details><summary>LLOneBot</summary>

开启「反向 WebSocket」，添加地址 `ws://127.0.0.1:9090/onebot/v11/ws`。

</details>

适配器自动注册的可用端点，填其中任意一个都可以：

| 端点 | 说明 |
| --- | --- |
| `ws://127.0.0.1:9090/onebot/v11/ws` | 反向 WebSocket（推荐） |
| `ws://127.0.0.1:9090/onebot/v11/` | 反向 WebSocket（根路径） |
| `ws://127.0.0.1:9090/onebot/v11/ws/` | 同上，带结尾斜杠 |
| `http://127.0.0.1:9090/onebot/v11/http` | HTTP POST 上报（还需配 `ONEBOT_API_ROOTS`） |

#### 方式二：正向 WebSocket

NoneBot 主动连到协议端的 WebSocket 服务器。这条路需要给 NoneBot 换一个
**带 WebSocket 客户端**的驱动器 —— 默认驱动器只有 `ReverseMixin`，连不出去。

1. 在协议端开启「正向 WebSocket / WebSocket 服务器」，记下端口（例如 `3001`）。
2. 在 [.env](.env) 里加两行：

```
DRIVER=~fastapi+~websockets
ONEBOT_WS_URLS=["ws://127.0.0.1:3001"]
```

`~fastapi+~websockets` 是 NoneBot 的混合驱动器，在保留反向 WS 能力的同时
加上正向 WS 能力；只写 `~websockets` 会让 NoneBot 不再监听 9090 端口。

#### 配置访问令牌

若协议端开了 token，在 [.env](.env) 里配置相同的值。下面两种写法等价
（分别是适配器配置项的别名和字段名），任选其一：

```
ONEBOT_ACCESS_TOKEN="你的token"
# 等价写法
ONEBOT_V11_ACCESS_TOKEN="你的token"
```

> `accounts/` 目录里的是旧版 `go-cqhttp` 的配置文件，现已不再使用，可以留着或自行删除。

### 5. 使用

向机器人发送 `/info` 查看机器人信息。

---

## 项目结构

```
bot.py                 启动入口（注册 OneBot V11 适配器）
pyproject.toml         项目元数据 + [tool.nonebot] 插件目录配置
requirements.txt       依赖清单
.env / .env.prod / .env.dev   环境与机器人配置
utils/                 通用工具（配置读取、权限、消息合并转发）
path/path.py           各种数据文件路径
src/plugins/           插件目录
    pixiv/             涩图 + 幻影坦克合成
    help/              机器人信息
    reply/             自动回复（青云客）
    passive_skills/    被动技能
    destiny2/          日报（需可选依赖 playwright）
    emoticon/          表情包
    reptile/           爬虫（已停用）
    search_pictures/   以图搜图（已停用）
    scold/             骂人（已停用）
    admin/             管理（已停用）
data/                  机器人数据
menu_config/           菜单配置
```

---

## 本次修复记录

项目长期未更新，为重新跑起来做了以下修改：

1. **`bot.py`**：恢复被注释掉的 OneBot V11 适配器注册；控制台适配器改为通过
   `ENABLE_CONSOLE_ADAPTER` 按需启用（避免占用终端 TUI）。
2. **`pyproject.toml`**：`[tool.poetry]` 迁移到 PEP 621 的 `[project]`；
   Python 要求 `^3.7.3` → `>=3.9`；`nonebot2` `^2.0.0-beta.1` → `>=2.4.4`；
   `[tool.nonebot]` 升级为 nb-cli 1.x 新格式（消除 legacy format 警告）。
3. **新增 `requirements.txt`**：README 一直在引用但文件并不存在。
4. **`utils/utils_def.py`**：移除无 fallback 的 `import ujson as json`
   （ujson 无 Python 3.14 轮子，且该行会被下一行的标准库 `json` 覆盖）。
5. **`src/plugins/pixiv/constant.py`**：整个文件原本被注释掉，导致
   `make_new_image` / `func` 导入失败、pixiv 插件无法加载。现已按
   Pillow 12 / numpy 2.x 的 API 恢复，并：
   * `Image.ANTIALIAS` / `Image.NEAREST` → `Image.Resampling.LANCZOS` / `.NEAREST`
     （Pillow 10 起移除）
   * 字体从裸文件名 `simhei.ttf` 改为按候选路径加载，找不到时退回内置字体
6. **`src/plugins/pixiv/__init__.py`**：`nonebot.internal.params` →
   `nonebot.params`（前者已废弃）。
7. **`src/plugins/destiny2/__init__.py`**：`async_playwright` 原本未导入会抛
   `NameError`，现改为懒加载并在缺失时给出明确提示。
8. **`.env.prod`**：文件开头带 UTF-8 BOM，导致配置里多出一个 `\ufeffhost` 键，
   已重存为无 BOM 的 UTF-8。

---

## 写在最后

本项目是自己娱乐所用同时从中学习。

项目部分代码思想和资源借鉴于 [真寻Bot](https://github.com/HibiKier/zhenxun_bot)

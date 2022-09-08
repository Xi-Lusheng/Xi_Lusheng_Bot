# <center>汐鹿生Bot</center>

---

## 关于项目

**此项目基于 Python [Nonebot2库](https://v2.nonebot.dev/) 和 [go-cqhttp](https://docs.go-cqhttp.org/) 开发Q群机器人**

---

### 前言

此项目仅用于学习交流，请勿用于非法用途

---

## 关于项目

**安装bot所有功能，你需要做以下准备：**

* Python 版本 >= 3.8
* 配置 [ffmpeg](https://ffmpeg.org/) (发送语音必备的)环境变量
* 一台服务器
* 一些百度/Google和阅读官方文档的能力

由于本项目项目已经安装 [nonebot_plugin_gocqhttp](https://github.com/mnixry/nonebot-plugin-gocqhttp) 插件

所以不需要额外下载配置 `go-cqhttp` 客户端文件

---

## 运行项目

**安装依赖包**

```
pip install -r requirements.txt
```

**修改机器人配置，打开 .env.prod 文件**

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
```

详细配置请阅读 [nonebot](https://v2.nonebot.dev/) 官方文档

其它配置已在文件中使用注释表明，请自行配置

**启动机器人**

```
python bot.py
# or
nb run
```

第一次启动会生成一些插件的配置文件请耐心等待

启动成功后访问 `http://127.0.0.1:8080/go-cqhttp/#/` 配置机器人qq
账号和登录密码

详细参考 [nonebot_plugin_gocqhttp](https://github.com/mnixry/nonebot-plugin-gocqhttp) 配置

配置完成后重新启动机器人即可


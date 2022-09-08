# <center>汐鹿生Bot</center>

---

## 关于项目

**此项目基于 Python [Nonebot2](https://v2.nonebot.dev/) 和 [go-cqhttp](https://docs.go-cqhttp.org/) 开发Q群机器人**

---

### 前言

此项目仅用于学习交流，请勿用于非法用途

项目配置过程中可能会遇到各种奇怪的错误，如果没有一些基础和耐心的话是永远走不出第一步的

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

**修改机器人配置，打开 `.env.dev` 文件**

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

**打开 `.env` 文件，将 `ENVIRONMENT` 修改为**

```
ENVIRONMENT=dev
```

详细配置请阅读 [nonebot2](https://v2.nonebot.dev/) 官方文档

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

向机器人发送 `菜单` 查看目前功能，详细查看 [nonebot_plugin_PicMenu](https://github.com/hamo-reid/nonebot_plugin_PicMenu) 插件介绍

由于部分功能使用的是他人的插件，请自行阅读插件介绍与配置

* [nonebot_plugin_gocqhttp](https://github.com/mnixry/nonebot-plugin-gocqhttp)
* [nonebot_plugin_ygo](https://github.com/anlen123/nonebot_plugin_ygo)
* [nonebot_plugin_repeater](https://github.com/ninthseason/nonebot-plugin-repeater)
* [nonebot_plugin_remake](https://github.com/noneplugin/nonebot-plugin-remake)
* [nonebot_plugin_baidutranslate](https://github.com/NumberSir/nonebot_plugin_baidutranslate)
* [nonebot_plugin_abstract](https://github.com/CherryCherries/nonebot-plugin-abstract)
* [nonebot_plugin_crazy_thursday](https://github.com/MinatoAquaCrews/nonebot_plugin_crazy_thursday)
* [nonebot_plugin_gspanel](https://github.com/monsterxcn/nonebot-plugin-gspanel)
* [nonebot_plugin_gsmaterial](https://github.com/monsterxcn/nonebot-plugin-gsmaterial)
* [nonebot_plugin_PicMenu](https://github.com/hamo-reid/nonebot_plugin_PicMenu)
* [nonebot_plugin_setu](https://github.com/ayanamiblhx/nonebot_plugin_setu)

## 写在最后

本项目是自己娱乐所用同时从中学习，我自己也才学Python不久，希望有大佬能指点我项目不足的地方

项目部分代码思想和资源借鉴于 [真寻Bot](https://github.com/HibiKier/zhenxun_bot) 

我不能保证我写的代码一点问题都没有，所以如果有代码问题或者什么建议还请在issue处告诉我

后续自己还好更新其它更多的功能，敬请期待吧


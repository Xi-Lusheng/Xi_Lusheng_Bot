#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

import nonebot

# OneBot V11 适配器：连接 NapCat / Lagrange.OneBot / LLOneBot 等新版客户端
from nonebot.adapters.onebot.v11 import Adapter as OneBotV11Adapter

nonebot.init()
app = nonebot.get_asgi()

driver = nonebot.get_driver()

driver.register_adapter(OneBotV11Adapter)

# 控制台适配器仅用于本地无 QQ 客户端时调试，会占用终端 TUI，默认关闭。
# 需要时在 .env / .env.prod 中设置 ENABLE_CONSOLE_ADAPTER=true
if os.getenv("ENABLE_CONSOLE_ADAPTER", "").strip().lower() in ("1", "true", "yes", "on"):
    from nonebot.adapters.console import Adapter as ConsoleAdapter

    driver.register_adapter(ConsoleAdapter)

nonebot.load_from_toml("pyproject.toml")


if __name__ == "__main__":
    nonebot.logger.warning("Always use `nb run` to start the bot instead of manually running!")
    nonebot.run(app="__mp_main__:app")

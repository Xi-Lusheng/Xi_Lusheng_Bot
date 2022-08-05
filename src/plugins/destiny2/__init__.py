from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot, Message

import urllib3
import json

today = on_command("today", aliases={'日报', }, priority=5)


@today.handle()
async def handle_first_receive(event: GroupMessageEvent, message: Message = CommandArg()):
    try:
        try:
            url = 'http://www.tianque.top/d2api/today/'

            r = urllib3.PoolManager().request('GET', url)
            hjson = json.loads(r.data.decode())

            img_url = hjson["img_url"]

            cq = "[CQ:image,file=" + img_url + ",id=40000]"

            await today.send(Message(cq))
        except:
            url = 'http://www.tianque.top/d2api/today/'

            r = urllib3.PoolManager().request('GET', url)
            hjson = json.loads(r.data.decode())

            error_url = hjson["error"]
            await today.send("获取日报失败\n" +
                             "error:\n" +
                             error_url)
    except:
        await today.send("获取日报失败:\n服务器错误")

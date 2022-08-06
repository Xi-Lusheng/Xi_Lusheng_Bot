from pathlib import Path
import os
import random
import nonebot
import requests

try:
    import ujson as json
except ModuleNotFoundError:
    import json
from httpx import AsyncClient
import re

Bot_NICKNAME: str = list(nonebot.get_driver().config.nickname)[0]  # bot的nickname
Bot_MASTER: str = list(nonebot.get_driver().config.superusers)[0]  # bot的主人名称

# 载入词库(这个词库有点涩)
AnimeThesaurus = json.load(open(Path(os.path.join(os.path.dirname(
    __file__), "data")) / "data.json", "r", encoding="utf8"))

# hello之类的回复
hello__reply = [
    "你好！",
    "哦呀？！",
    "你好！Ov<",
    f"库库库，呼唤{Bot_NICKNAME}做什么呢",
    "我在呢！",
    "呼呼，叫俺干嘛",
]

# 戳一戳消息
poke__reply = [
    "lsp你再戳？",
    "连个可爱美少女都要戳的肥宅真恶心啊。",
    "你再戳！",
    "？再戳试试？",
    "别戳了别戳了再戳就坏了555",
    "我爪巴爪巴，球球别再戳了",
    "你戳你🐎呢？！",
    f"请不要戳{Bot_NICKNAME} >_<",
    "放手啦，不给戳QAQ",
    f"喂(#`O′) 戳{Bot_NICKNAME}干嘛！",
    "戳坏了，赔钱！",
    "戳坏了",
    "嗯……不可以……啦……不要乱戳",
    "那...那里...那里不能戳...绝对...",
    "(。´・ω・)ん?",
    "有事恁叫我，别天天一个劲戳戳戳！",
    "欸很烦欸！你戳🔨呢",
    "再戳一下试试？",
    "啊呜，太舒服刚刚竟然睡着了。什么事？",
]


# 从字典里返还消息
async def get_chat_result(text: str, nickname: str) -> str:
    if len(text) < 7:
        keys = AnimeThesaurus.keys()
        for key in keys:
            if text.find(key) != -1:
                return random.choice(AnimeThesaurus[key]).replace("你", nickname)


# 调用思知机器人
si_zhi_url = 'https://api.ownthink.com/bot'
appid = '346f5fd729d98a99aeadea97c9c71966'


async def get_n(text):
    try:
        data = {
            "spoken": text,
            "appid": appid,
            "userid": "ZubDg1Ad"
        }
        r = requests.post(si_zhi_url, data=json.dumps(data))
        result = json.loads(r.content)
        message = result['data']['info']['text']
        return message
    except KeyError:
        return '这个问题好头疼呀，问点别的叭'

import random
import requests
from path.path import AnimeThesaurus, Util_Json
from utils.config import Bot_MASTER, Bot_NICKNAME

try:
    import ujson as json
except ModuleNotFoundError:
    import json


# 从字典里返还消息
async def get_chat_result(text: str, nickname: str) -> str:
    if len(text) < 20:
        keys = AnimeThesaurus.keys()
        for key in keys:
            if text.find(key) != -1:
                return random.choice(AnimeThesaurus[key]).replace("你", nickname).replace("Bot_MASTER", Bot_MASTER)


async def utils_get_chat_result(text: str) -> str:
    if len(text) < 20:
        keys = Util_Json.keys()
        for key in keys:
            if text.find(key) != -1:
                return random.choice(Util_Json[key])


# 调用青云客机器人
async def get_message(text: str) -> str:
    try:
        url = 'http://api.qingyunke.com/api.php'
        data = {
            'key': 'free',
            'appid': 0,
            'msg': text
        }
        r = requests.get(url, params=data)
        result = json.loads(r.content)
        message = (result['content']).replace('菲菲', Bot_NICKNAME)
        return message
    except KeyError:
        return '这个问题好头疼呀，问点别的叭'

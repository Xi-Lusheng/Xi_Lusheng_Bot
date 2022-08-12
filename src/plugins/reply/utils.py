from pathlib import Path
import os
import random
import requests
from utils.config import app_id, user_id

try:
    import ujson as json
except ModuleNotFoundError:
    import json

# 载入词库(这个词库有点涩)
AnimeThesaurus = json.load(open(Path(os.path.join(os.path.dirname(
    __file__), "data")) / "data.json", "r", encoding="utf8"))

Util_Json = json.load(open(Path(os.path.join(os.path.dirname(
    __file__), "data")) / "utils_data.json", "r", encoding="utf8"))


# 从字典里返还消息
async def get_chat_result(text: str, nickname: str) -> str:
    if len(text) < 10:
        keys = AnimeThesaurus.keys()
        for key in keys:
            if text.find(key) != -1:
                return random.choice(AnimeThesaurus[key]).replace("你", nickname)


async def utils_get_chat_result(text: str) -> str:
    if len(text) < 10:
        keys = Util_Json.keys()
        for key in keys:
            if text.find(key) != -1:
                return random.choice(Util_Json[key])


# 调用思知机器人
async def get_n(text):
    si_zhi_url = 'https://api.ownthink.com/bot'
    try:
        data = {
            "spoken": text,
            "appid": app_id,
            "userid": user_id,
        }
        r = requests.post(si_zhi_url, data=json.dumps(data))
        result = json.loads(r.content)
        message = result['data']['info']['text']
        return message
    except KeyError:
        return '这个问题好头疼呀，问点别的叭'

import random
import requests
from path.path import AnimeThesaurus, Util_Json
from utils.config import app_id, user_id
try:
    import ujson as json
except ModuleNotFoundError:
    import json


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

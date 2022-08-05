import json
import requests
from nonebot import on_message
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import Event

# 思知机器人
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


AI_reply = on_message(rule=to_me(), priority=99)


@AI_reply.handle()
async def reply(event: Event):
    if event.is_tome() and int(event.get_user_id()) != event.self_id:
        say = event.get_message()
        say = await get_n(str(say))
        await AI_reply.finish(message=say)

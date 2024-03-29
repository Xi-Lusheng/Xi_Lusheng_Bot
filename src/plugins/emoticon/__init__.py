import re
import random
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot import on_message
from src.plugins.emoticon.constant import get_emo


emo = on_message(priority=96, block=False)


@emo.handle()
async def emo_(event: MessageEvent):
    if random.randint(0, 10) > 7:
        msg = str(event.get_message())
        msg = re.sub(r"\[.*?\]", "", msg)
        emo_path = await get_emo(msg)
        if emo_path:
            await emo.finish(emo_path)





import os
import random
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot import on_keyword, on_regex
from nonebot.rule import to_me
from path.path import ding_gong_path
from utils.utils_def import record

scold = on_keyword({'骂'}, rule=to_me(), priority=5, block=True)


@scold.handle()
async def scold_(event: MessageEvent):
    if len(str((event.get_message()))) > 1:
        voice = random.choice(os.listdir(ding_gong_path))
        result = record(voice, 'ding_gong')
        await scold.send(result)
        await scold.finish(voice.split("_")[1])

sakana = on_regex('sakana', rule=to_me(), priority=5, block=True)


@sakana.handle()
async def sakana_(event: MessageEvent):
    if len(str((event.get_message()))) > 1:
        result = record('sakana.mp3', 'comic_voice')
        await sakana.finish(result)

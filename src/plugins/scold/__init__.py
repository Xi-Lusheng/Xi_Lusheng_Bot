import os
import random
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot import on_keyword
from nonebot.rule import to_me
from path.path_utils import scold_data_path
from utils.utils_def import record

scold = on_keyword({'骂'}, rule=to_me(), priority=5, block=True)


@scold.handle()
async def scold_(event: MessageEvent):
    if len(str((event.get_message()))) > 1:
        voice = random.choice(os.listdir(scold_data_path))
        result = record(voice)
        await scold.send(result)
        await scold.send(voice.split("_")[1])



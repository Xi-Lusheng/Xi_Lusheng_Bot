import json
import random
import re

import requests

from path.path import AnimeThesaurus, Util_Json
from utils.config import Bot_MASTER, Bot_NICKNAME


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
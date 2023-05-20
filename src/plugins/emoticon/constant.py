from nonebot.adapters.onebot.v11 import MessageSegment
from path.path import emo_data_path
import os


async def get_emo(msg: str) -> MessageSegment:
    if len(msg) < 20:
        dic = {
            i.split('.')[0]: emo_data_path / i for i in os.listdir(emo_data_path)
        }
        for key in dic.keys():
            if msg.find(key) != -1:
                result = MessageSegment.image(dic[key])
                return result

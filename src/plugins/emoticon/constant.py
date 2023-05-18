from nonebot.adapters.onebot.v11 import MessageSegment
from path.path import emo_data_path
import os


async def get_emo(msg: str) -> MessageSegment:
    if len(msg) < 20:
        names = os.listdir(emo_data_path)
        for i in names:
            name = i.split('.')[0]
            path = emo_data_path / i
            dic = {
                name: path
            }
            keys = dic.keys()
            for key in keys:
                if msg.find(key) != -1:
                    result = MessageSegment.image(dic[key])
                    return result

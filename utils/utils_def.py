from pathlib import Path
from typing import List, Union
from nonebot import logger
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent, Bot, Message, MessageSegment
import ujson as json
import json
from path.path import scold_data_path
import re


# 消息合并转发
async def send_forward_msg_group(
        bot: Bot,
        event: MessageEvent,
        name: str,
        msgs: [],
):
    def to_json(msg):
        return {"type": "node", "data": {"name": name, "uin": bot.self_id, "content": msg}}

    messages = [to_json(msg) for msg in msgs]
    if isinstance(event, GroupMessageEvent):
        await bot.call_api(
            "send_group_forward_msg", group_id=event.group_id, messages=messages
        )
    else:
        await bot.call_api(
            "send_private_forward_msg", user_id=event.user_id, messages=messages
        )


def get_message_img(data: Union[str, Message]) -> List[str]:
    """
    说明:
        获取消息中所有的 图片 的链接
    参数:
        :param data: event.json()
    """
    img_list = []
    if isinstance(data, str):
        data = json.loads(data)
        for msg in data["message"]:
            if msg["type"] == "image":
                img_list.append(msg["data"]["url"])
    else:
        for seg in data["image"]:
            img_list.append(seg.data["url"])
    return img_list


def record(voice_name: str, path: str = None) -> MessageSegment or str:
    """
    说明：
        生成一个 MessageSegment.record 消息
    参数：
        :param voice_name: 音频文件名称，默认在 data/scold_data 目录下
        :param path: 音频文件路径，默认在 data/scold_data 目录下
    """
    if len(voice_name.split(".")) == 1:
        voice_name += ".mp3"
    file = (
        Path(scold_data_path) / path / voice_name
        if path
        else Path(scold_data_path) / voice_name
    )
    if "http" in voice_name:
        return MessageSegment.record(voice_name)
    if file.exists():
        result = MessageSegment.record(f"file:///{file.absolute()}")
        return result
    else:
        logger.warning(f"语音{file.absolute()}缺失...")
        return ""


def face(id_: int) -> MessageSegment:
    """
    说明:
        生成一个 MessageSegment.face 消息
    参数:
        :param id_: 表情id
    """
    return MessageSegment.face(id_)


class GetRe:
    """
    正则匹配消息
    """
    def __init__(self, raw_message):
        self._raw_message = raw_message
        self._get_msg_id = re.compile(r"\[CQ:reply,id=(-?\d*)]")
        self._get_at_id = re.compile(r"\[CQ:at,qq=(\d*)]")
        self._get_cd = re.compile(r"cd(\d*)")

    def get_msg_id(self):
        """
        获取消息id
        :return: re变量，使用group获取
        """
        msg_id = self._get_msg_id.search(self._raw_message)
        return msg_id

    def get_at_id(self):
        """
        获取@人qq号
        :return: re变量，使用group获取
        """
        at_id = self._get_at_id.search(self._raw_message)
        return at_id

    def get_cd(self):
        """
        获取消息中的cd时间
        :return: re变量，使用group获取
        """
        cd = self._get_cd.search(self._raw_message)
        return cd


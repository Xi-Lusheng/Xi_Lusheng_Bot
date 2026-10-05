import json

import httpx
from nonebot import logger

from utils.config import Bot_NICKNAME


def lolicon(N: int = 1, Tag: str = "", R18: int = 0):
    if Tag:
        tag_list = Tag.strip().split()
        tag = "&tag="
        for seg in tag_list[:3]:
            tag += f"{seg}|"
        else:
            tag = tag[:-1]
    else:
        tag = ""

    msg = ""
    if 1 <= N <= 10:
        msg += f"{Bot_NICKNAME}为你准备了{N}张随机{'r18' if R18 else ''}{tag[5:]}色图。"
    elif N > 10:
        N = 1
        if R18 == 1:
            msg += f"{Bot_NICKNAME}为你的身体着想，为你准备了一张随机r18{tag[5:]}色图。"
        else:
            msg += f"{Bot_NICKNAME}被禁止单次发送超过10张色图...但是，{Bot_NICKNAME}为你准备了一张随机{tag[5:]}色图。"
    else:
        N = 1
        msg += f"{Bot_NICKNAME}接收到了奇怪的数量参数，不过{Bot_NICKNAME}送你一张随机{'r18' if R18 == 1 else ''}{tag[5:]}色图。"
    logger.info(f"正在从 Lolicon API 获取图片。")
    resp = httpx.get(f"https://api.lolicon.app/setu/v2?num={N}&r18={R18}{tag}")
    if resp.status_code == 200:
        resp = resp.text
        resp = ''.join(x for x in resp if x.isprintable())
        lolicon_list = json.loads(resp)["data"]
        image_list = []
        if lolicon_list:
            N = len(lolicon_list)
            for i in range(N):
                image_list.append({
                    "pixiv_id": lolicon_list[i]["pid"],
                    "url": lolicon_list[i]["urls"]["original"],
                    "r18": lolicon_list[i]["r18"]
                })
        else:
            msg = f"没有找到【{tag}】"
    else:
        logger.info(f"从 Lolicon API 获取图片失败，status_code：{resp.status_code}")
        msg = "连接出错了..."
        image_list = None
    return msg, image_list


def xi_lusheng(N: int = 1, R18: int = 0):
    msg = ""
    if 1 <= N <= 10:
        msg += f"{Bot_NICKNAME}为你准备了{N}张随机{'r18' if R18 == 2 else ''}色图。"
    elif N > 10:
        N = 1
        if R18 == 2:
            msg += f"{Bot_NICKNAME}为你的身体着想，为你准备了一张随机r18色图。"
        else:
            msg += f"{Bot_NICKNAME}被禁止单次发送超过10张色图...但是，{Bot_NICKNAME}为你准备了一张随机色图。"
    else:
        N = 1
        msg += f"{Bot_NICKNAME}接收到了奇怪的数量参数，不过{Bot_NICKNAME}送你一张随机{'r18' if R18 == 2 else ''}色图。"
    logger.info(f"正在从 Xi_Lusheng API 获取图片。")
    resp = httpx.get(f"https://api.xilusheng.top/nonebot/pixiv/random/?num={N}&sort={R18}")
    if resp.status_code == 200:
        resp = resp.text
        resp = ''.join(x for x in resp if x.isprintable())
        lusheng_list = json.loads(resp)["data"]
        image_list = []
        if lusheng_list:
            N = len(lusheng_list)
            for i in range(N):
                image_list.append({
                    "pixiv_id": lusheng_list[i]["id"],
                    "url": lusheng_list[i]["image"],
                    "r18": True if lusheng_list[i]["sort"] == "r18" else False
                })
        else:
            msg = f"没有找到图片"
    else:
        logger.info(f"从 Xi_Lusheng API 获取图片失败，status_code：{resp.status_code}")
        msg = "连接出错了..."
        image_list = None
    return msg, image_list


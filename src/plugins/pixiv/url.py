"""Lolicon API（https://api.lolicon.app/setu/v2）调用封装。

【本模块只干一件事】
    把 (数量, 标签, R18) 变成 (给用户看的文案, 图片元数据列表)。
    不下载图片、不发消息、不关心消息怎么发——那些在 __init__.py / constant.py 里。

【返回值约定（很重要，调用方只依赖这两个）】
    成功 -> ("初号姬为你准备了N张…", [{"pixiv_id": int, "url": str, "r18": bool}, ...])
    失败 -> ("连接出错了..." / "没有找到【xx】", [])
    也就是：图片列表永远是 list，不再出现 None。
"""

from __future__ import annotations

import json
from typing import Any
from urllib.parse import quote

import httpx
from nonebot import logger

from utils.config import Bot_NICKNAME
from utils.net import get as http_get

API_ENDPOINT = "https://api.lolicon.app/setu/v2"

MAX_IMAGES = 3  # 单次最多请求/发送 3 张，超过只发 1 张（原来是 10，单次太多会把内存打爆）
MAX_TAGS = 3  # Lolicon API 最多同时接受 3 个 tag
DEFAULT_API_NAME = "lolicon API"

# 图片元数据在项目内部的统一形状
ImageInfo = dict[str, Any]


def _parse_tag(tag: str) -> tuple[str, str]:
    """把用户输入的标签拆成 (请求参数, 展示文案) 两份。

    【效果】输入 "白丝 萝莉"：
        请求参数 -> "&tag=白丝|萝莉"   （Lolicon API 用 | 连接多个 tag，最多 3 个）
        展示文案 -> "白丝|萝莉"        （拼进"…为你准备了随机xx色图"）

    【为什么拆成两份】
    原实现只有一份字符串 tag，先在循环里拼出 "白丝|萝莉|" 再 tag[:-1] 去掉尾巴，
    用户看到的文案又靠 tag[5:] 这种魔术切片把 "&tag=" 前缀切掉。
    两边共用一个变量，任何一处改格式就会同时把用户看到的文案改坏
    （"没有找到【xx】" 那里就漏切了，会显示成"没有找到【&tag=白丝】"）。
    现在参数和文案各算各的，互不影响。
    """

    tags = [t for t in tag.strip().split() if t][:MAX_TAGS]

    if not tags:
        return "", ""

    return "&tag=" + quote("|".join(tags), safe="|"), "|".join(tags)


def _build_notice(count: int, r18: int, tag_text: str) -> tuple[str, int]:
    """生成"初号姬为你准备了…"这句文案，并返回真正要请求的张数。

    【效果】把原来 if/elif/else 三个分支里重复了 4 遍的句子收成一个模板：

        count < 1   -> "接收到了奇怪的数量参数，不过…送你一张随机{r18}{tag}色图。" (返回 1)
        count > 10  -> r18 时"为你的身体着想…一张随机r18{tag}色图。"
                       非 r18 时"被禁止单次发送超过10张色图...但是…一张随机{tag}色图。" (返回 1)
        其它        -> "为你准备了{count}张随机{r18}{tag}色图。" (原样返回 count)
    """

    r18_text = "r18" if r18 else ""

    if count < 1:
        return (
            f"{Bot_NICKNAME}接收到了奇怪的数量参数，"
            f"不过{Bot_NICKNAME}送你一张随机{r18_text}{tag_text}色图。",
            1,
        )

    if count > MAX_IMAGES:
        if r18:
            return (
                f"{Bot_NICKNAME}为你的身体着想，为你准备了一张随机r18{tag_text}色图。",
                1,
            )
        return (
            f"{Bot_NICKNAME}被禁止单次发送超过{MAX_IMAGES}张色图..."
            f"但是，{Bot_NICKNAME}为你准备了一张随机{tag_text}色图。",
            1,
        )

    return f"{Bot_NICKNAME}为你准备了{count}张随机{r18_text}{tag_text}色图。", count


def _decode(resp: httpx.Response) -> list[ImageInfo]:
    """把响应体解析成 ImageInfo 列表。

    【为什么先清洗再 json.loads】
    api.lolicon.app 经过部分代理/防火墙时会夹带回不可见的控制字符，
    直接 json.loads 会抛 JSONDecodeError。原实现用
    ''.join(x for x in text if x.isprintable()) 清洗，这里保留同样的行为。
    """

    text = "".join(ch for ch in resp.text if ch.isprintable())
    payload = json.loads(text)

    items = (payload or {}).get("data") or []

    return [
        {
            "pixiv_id": item["pid"],
            "url": item["urls"]["original"],
            "r18": item["r18"],
        }
        for item in items
    ]


def lolicon(N: int = 1, Tag: str = "", R18: int = 0) -> tuple[str, list[ImageInfo]]:
    """向 Lolicon API 请求涩图元数据。

    【失败也返回空列表，原因】
    原实现在 HTTP 非 200 时把 image_list 设成 None 返回。调用方紧接着写

        url_list = [i['url'] for i in data]

    于是抛 TypeError: 'NoneType' object is not iterable，
    真正的错误（"连接出错了..."）被完全盖掉，我们在日志里只看到一行看不懂的 TypeError。
    现在统一返回 []，调用方一句 if not images 就能收口。
    """

    tag_query, tag_text = _parse_tag(Tag)
    notice, count = _build_notice(N, R18, tag_text)
    url = f"{API_ENDPOINT}?num={count}&r18={R18}{tag_query}"

    logger.info(f"正在从 Lolicon API 获取图片：{url}")

    try:
        # utils/net.get：默认 3 次重试 + 20s 超时。
        # 图源域名（api.lolicon.app / i.pixiv.re）会偶发 DNS 解析失败，
        # 报错形如 [Errno -2] Name or service not known / [Errno 11001] getaddrinfo failed，
        # 重试能把这种一两秒的抖动直接吃掉。
        resp = http_get(url)
    except Exception as exc:
        logger.warning(f"请求 Lolicon API 失败：{type(exc).__name__}: {exc}")
        return "连接出错了...", []

    if resp.status_code != 200:
        logger.warning(f"Lolicon API 返回 HTTP {resp.status_code}")
        return "连接出错了...", []

    try:
        images = _decode(resp)
    except (ValueError, KeyError, TypeError) as exc:
        logger.warning(f"Lolicon API 返回内容无法解析：{type(exc).__name__}: {exc}")
        return "连接出错了...", []

    if not images:
        return f"没有找到【{tag_text}】", []

    return notice, images

"""涩图插件入口。

【整体流程】
    用户「来3张白丝涩图」
        -> _parse_count / _parse_tag 拆出 (数量, 标签)
        -> url.lolicon() 只负责拿到图片元数据（pid / url / r18）
        -> constant.func() 并发下载原图 bytes
        -> constant.make_new_image() 逐张合成幻影坦克（CPU 活，丢线程池）
        -> utils_def.send_forward_msg_group() 合并转发成一张卡片

【本文件的职责】只做"解析输入 → 调度模块 → 拼消息"的编排，不写像素、不写 HTTP。
"""

import asyncio
import re
import unicodedata

import httpx
from nonebot import logger, on_regex
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    MessageEvent,
    MessageSegment,
)
from nonebot.exception import FinishedException
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata

from src.plugins.pixiv.constant import func, make_new_image
from src.plugins.pixiv.url import DEFAULT_API_NAME, lolicon
from src.plugins.pixiv.utils import customer_api, get_session
from src.plugins.pixiv.utils import set_r18 as set_session_r18
from utils.config import Bot_NICKNAME
from utils.utils_def import send_forward_msg_group

__plugin_meta__ = PluginMetadata(
    name='涩图',
    description='发送动漫图片',
    usage='',
    extra={
        'menu_data': [
            {
                'func': '涩图',
                'trigger_method': 'on_re',
                'trigger_condition': '来N张(r18)xx色图',
                'brief_des': '发送指定图片',
                'detail_des': '发送二指定图片，N代表数量，加上r18将发送r18图片（群聊不允许查看r18），xx为指定图片tag'
            },
        ],
        'menu_template': 'default'
    }
)

setu = on_regex("^来.*[点张份].+$", priority=10, block=True)

# 全局涩图并发闸门：值为 1 表示同一时刻只跑一条涩图流程（理由见 setu_ 内的注释）。
_SETU_LOCK = asyncio.Semaphore(1)


# ---------------------------------------------------------------------------
# 输入解析
# ---------------------------------------------------------------------------

# 「来3张白丝涩图」-> 先砍前缀"来"和"张…"之后的部分，正好剩下数量
_COUNT_RE = re.compile(r"^来|[张份].+$")
# 同一个句子 -> 砍掉"来…张/份/点"，剩下的就是标签
_TAG_RE = re.compile(r"^来|.*[张份]")


def _parse_count(cmd: str) -> int:
    """从「来3张白丝涩图」解析出 3。

    【效果】三条兜底路径，任何一种都能走到：
        纯数字        "3"    -> int("3") = 3
        中文数字      "三"    -> unicodedata.numeric => 3
        识别不了      "好多"  -> 0

    返回 0 不用在这里报错：url._build_notice 会把"数量 < 1"统一
    变成「接收到了奇怪的数量参数…送你一张随机涩图」，文案只有一处。
    """

    raw = _COUNT_RE.sub("", cmd)
    if not raw:
        return 1

    try:
        return int(raw)
    except ValueError:
        pass

    try:
        return int(unicodedata.numeric(raw))
    except (TypeError, ValueError):
        return 0


def _parse_tag(cmd: str) -> str:
    """从「来3张白丝涩图」解析出标签「白丝」。

    【效果】"来3张白丝涩图" -> "白丝"；"来一份r18萝莉色图" -> "r18萝莉"。
    结尾只剥「涩图/色图」两个字，中间的 tag 原样保留（由 url._parse_tag 按空格切分）。
    """

    tag = _TAG_RE.sub("", cmd).strip()
    if tag.endswith(("涩图", "色图")):
        tag = tag[:-2]
    return tag.strip()


def _session_id(event: MessageEvent) -> str:
    """配置隔离用的 key：群聊取群号，私聊取 QQ 号。"""

    if isinstance(event, GroupMessageEvent):
        return str(event.group_id)
    return event.get_user_id()


# ---------------------------------------------------------------------------
# 发图
# ---------------------------------------------------------------------------

@setu.handle()
async def setu_(bot: Bot, event: MessageEvent):
    cmd = event.get_plaintext()
    count = _parse_count(cmd)
    tag = _parse_tag(cmd)

    # get_session：取不到（第一次用）就补一份默认配置并落盘，
    # 所以这里不再需要"手动 if id_ not in customer_api"再赋值。
    session_id = _session_id(event)
    session = get_session(session_id)
    api = session.get("url", DEFAULT_API_NAME)

    r18 = 0
    if tag.startswith("r18"):
        if session.get("r18"):
            tag = tag[3:].strip()
            r18 = 1
        else:
            await setu.send(
                f"管理员关闭了r18功能哦，但是{Bot_NICKNAME}还是为你准备了非r18的涩图"
            )

    try:
        # lolicon() 现在保证第二项永远是 list：失败时是 []，不会返回 None。
        msg, images = lolicon(count, tag, r18)
        if not images:
            await setu.finish(msg, at_sender=True)

        await setu.send(f"{msg}\n图片取自：{api}", at_sender=True)

        # 【并发闸门】同一时刻只允许一条涩图流程占用内存。
        # 单张 1000000 像素的 float32 幻影坦克合成峰值约 70~95MB，
        # 而 2026-10-10 服务器死机就是多条请求同时跑把 1.7GB 内存打爆、导致整机 thrash。
        # 串行化后再多请求也只是排队，不会同时占用多份大数组。
        async with _SETU_LOCK:
            # 并发下载。func 内部已经吃掉了异常并返回 None，不会中断 gather。
            async with httpx.AsyncClient(timeout=30.0) as client:
                raw_list = await asyncio.gather(*(func(client, i["url"]) for i in images))

            # 关键：把 (元数据, 原图) 成对过滤，而不是先过滤出 image_list 再 zip。
            # 原实现 zip(new_list, data) 在两图之间夹着失败项时会整体错位，
            # 结果就是"幻影坦克的图和下方显示的 pixiv_id/链接对不上"。
            downloaded = [(info, raw) for info, raw in zip(images, raw_list) if raw]
            if not downloaded:
                await setu.finish("获取图片失败。", at_sender=True)

            msg_list = []
            for info, raw in downloaded:
                # make_new_image 是同步的 numpy/PIL 计算，单张约几百毫秒；
                # 丢进线程池逐张做，既不阻塞事件循环，也不会同时持有全部原图+输出图而爆内存。
                mirage = await asyncio.to_thread(make_new_image, raw)
                msg_list.append(
                    MessageSegment.text("芝士幻影坦克：\n")
                    + MessageSegment.image(mirage)
                    + MessageSegment.text(
                        f"\n图片id：{info['pixiv_id']}\n"
                        f"r18：{info['r18']}\n"
                        f"图片链接：{info['url']}"
                    )
                )

        await send_forward_msg_group(
            bot, event, name=f"{Bot_NICKNAME}", msgs=[m for m in msg_list if m]
        )

    except FinishedException:
        # setu.finish 就是靠这个异常中断 handler 的，必须原样放行
        raise
    except Exception as e:
        # 用 exception 而不是 error：保留完整堆栈，
        # 否则线上只会看到"出现错误：某个字符串"，根本定位不到是哪一步。
        logger.exception("涩图流程出错")
        await setu.finish("出现错误：" + str(e), at_sender=True)


# ---------------------------------------------------------------------------
# r18 开关
# ---------------------------------------------------------------------------

set_r18 = on_regex("^(开启|关闭)r18$", permission=SUPERUSER, priority=50, block=True)


@set_r18.handle()
async def _(event: MessageEvent):
    text = event.get_plaintext()
    session_id = _session_id(event)

    if text.startswith("开启"):
        set_session_r18(session_id, True)
        await set_r18.finish("r18已开启")
    elif text.startswith("关闭"):
        set_session_r18(session_id, False)
        await set_r18.finish("r18已关闭")
    else:
        await set_r18.finish("r18设置失败")

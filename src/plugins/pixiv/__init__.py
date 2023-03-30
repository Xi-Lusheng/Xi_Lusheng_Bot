import asyncio
import base64
import re
import httpx
import requests
import unicodedata
from nonebot import on_regex, on_command, logger
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.internal.params import ArgPlainText, Arg
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.exception import ActionFailed
from nonebot.adapters.onebot.v11 import MessageSegment, MessageEvent, GroupMessageEvent, PrivateMessageEvent
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State
from src.plugins.pixiv.constant import get_image, make_new_image, func

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

from src.plugins.pixiv.url import Lolicon
from src.plugins.pixiv.utils import customer_api, save
from utils.config import Bot_NICKNAME
from utils.utils_def import send_forward_msg_group

# pixiv = on_regex('^(二次元|涩图|色图|r18)$|^来点(二次元|涩图|色图|r18)$', block=True, priority=10)
#
#
# @pixiv.handle()
# async def pixiv_(event: MessageEvent):
#     msg = event.get_plaintext()
#     r18 = re.search('r18', msg)
#     r16 = re.search('(涩图|色图)', msg)
#     if r18:
#         await pixiv.send('请等待合成幻影坦克', at_sender=True)
#         data = await get_image(sort=2)
#         try:
#             message = await make_new_image(data)
#             image = MessageSegment.image(f"base64://{base64.b64encode(message['new_image'].getvalue()).decode()}")
#             result = image + MessageSegment.text(f"\n图片id：{message['image_id']}\n"
#                                                  f"图片链接：{message['image_url']}")
#             await pixiv.finish(result)
#         except (ActionFailed, ValueError):
#             await pixiv.send("合成失败将只发送原图链接")
#             await pixiv.finish(MessageSegment.text(f"图片id：{data['image_id']}\n"
#                                                    f"图片链接：{data['image_url']}"))
#     elif r16:
#         await pixiv.send('请等待合成幻影坦克', at_sender=True)
#         data = await get_image(sort=1)
#         try:
#             message = await make_new_image(data)
#             image = MessageSegment.image(f"base64://{base64.b64encode(message['new_image'].getvalue()).decode()}")
#             result = image + MessageSegment.text(f"\n图片id：{message['image_id']}\n"
#                                                  f"图片链接：{message['image_url']}")
#             await pixiv.finish(result)
#         except (ActionFailed, ValueError):
#             await pixiv.send("合成失败将只发送原图链接")
#             await pixiv.finish(MessageSegment.text(f"图片id：{data['image_id']}\n"
#                                                    f"图片链接：{data['image_url']}"))
#     else:
#         data = await get_image(sort=0)
#         try:
#             image = MessageSegment.image(data['image_url'])
#             result = image + MessageSegment.text(f"\n图片id：{data['image_id']}\n"
#                                                  f"图片链接：{data['image_url']}")
#             await pixiv.finish(result)
#         except ActionFailed:
#             await pixiv.send("图片发送失败可能被风控，将合成幻影坦克")
#             message = await make_new_image(data)
#             image = MessageSegment.image(f"base64://{base64.b64encode(message['new_image'].getvalue()).decode()}")
#             result = image + MessageSegment.text(f"\n图片id：{message['image_id']}\n"
#                                                  f"图片链接：{message['image_url']}")
#             await pixiv.finish(result)
#         except ValueError:
#             await pixiv.send("幻影坦克合成失败，将发送图片原链接")
#             await pixiv.finish(MessageSegment.text(f"图片id：{data['image_id']}\n"
#                                                    f"图片链接：{data['image_url']}"))


delete_image = on_command("删除图片", block=True, priority=10, permission=SUPERUSER)


@delete_image.handle()
async def delete_image_(state: T_State, msg: Message = CommandArg()):
    if text := msg.get("text"):
        state["param"] = text


@delete_image.got("param", prompt="请输入图片的id")
async def delete_image_(param: str = ArgPlainText("param")):
    re_id = re.match(r"id(\d*)", param.replace(" ", ""))
    url = f"https://api.xilusheng.top/nonebot/pixiv/{re_id.group(1)}/"
    result = requests.delete(url)
    if result.status_code == 204:
        await delete_image.finish('删除成功')
    elif result.json()['code'] == 404:
        await delete_image.finish('没有找到该图片')
    else:
        await delete_image.finish('发生未知错误')


update_image = on_command('修改分级', block=True, priority=10, permission=SUPERUSER)


@update_image.handle()
async def update_image_(state: T_State, msg: Message = CommandArg()):
    if text := msg.get("text"):
        state["param"] = text


@update_image.got("param", prompt="请输入图片的id和分级")
async def update_image_(foo: str = ArgPlainText("param")):
    try:
        re_message = re.match(r".*?id(?P<image_id>\d*).*?", foo.replace(" ", ""))
        image_id = re_message.group('image_id')
        re_sort = re.match(r".*?分级(?P<sort>(全龄|r16|r18)).*?", foo.replace(" ", ""))
        sort = re_sort.group('sort')
        print(sort)
        if image_id and sort:
            url = f"https://api.xilusheng.top/nonebot/pixiv//{image_id}/"
            if sort == "r18":
                sort = 2
            elif sort == "r16":
                sort = 1
            elif sort == "全龄":
                sort = 0
            else:
                await update_image.finish("请输入正确的分级参数，如：全龄|r16|r18")
            data = {
                "sort": sort
            }
            result = requests.patch(url, data=data)
            if result.status_code == 200:
                await update_image.finish('修改分级成功')
            elif result.status_code == 400:
                error = result.json()['data']
                await update_image.finish(error)
            else:
                await update_image.finish("发生未知错误")
        await update_image.finish("请输入正确参数格式，如：id 1 分级 全龄")
    except AttributeError:
        await update_image.finish("请输入正确参数格式，如：id 1 分级 全龄")


setu = on_regex("^来.*[点张份].+$", priority=10, block=True)


@setu.handle()
async def setu_(bot: Bot, event: MessageEvent):
    msg = ''
    url_list = []
    cmd = event.get_plaintext()
    N = re.sub(r'^来|[张份].+$', '', cmd)
    N = N if N else 1
    try:
        N = int(N)
    except ValueError:
        try:
            N = int(unicodedata.numeric(N))
        except (TypeError, ValueError):
            N = 0

    Tag = re.sub(r'^来|.*[张份]', '', cmd)
    Tag = Tag[:-2] if (Tag.endswith("涩图") or Tag.endswith("色图")) else Tag

    if Tag.startswith("r18"):
        Tag = Tag[3:]
        R18 = 1
    else:
        R18 = 0

    if isinstance(event, GroupMessageEvent):
        if R18:
            await setu.finish("涩涩是禁止事项！！")
        else:
            api = customer_api.get(str(event.user_id), None)
            if api == "Lolicon API":
                if not Tag:
                    msg, url_list = Lolicon(N, Tag, R18)
                else:
                    msg, url_list = Lolicon(N, '', R18)
                api = "Lolicon API"
            else:
                msg, url_list = Lolicon(N, '', R18)
    else:
        api = customer_api.get(str(event.user_id), None)
        if api == "Lolicon API":
            if not Tag:
                msg, url_list = Lolicon(N, Tag, R18)
            else:
                msg, url_list = Lolicon(N, '', R18)
            api = "Lolicon API"
        else:
            msg, url_list = Lolicon(N, '', R18)
    msg += f"\n图片取自：{api}\n"
    await setu.send(msg, at_sender=True)
    try:
        async with httpx.AsyncClient() as client:
            task_list = []
            for urls in url_list:
                task = asyncio.create_task(func(client, urls))
                task_list.append(task)
            image_list = await asyncio.gather(*task_list)
    except Exception as e:
        logger.error(e)
        await setu.finish(str(e), at_sender=True)

    image_list = [image for image in image_list if image]

    if image_list:
        N = len(image_list)
        msg_list = []
        for i in range(N):
            msg_list.append(MessageSegment.image(file=image_list[i]))
        if isinstance(event, GroupMessageEvent):
            await send_forward_msg_group(bot, event, name=f'{Bot_NICKNAME}', msgs=[msg for msg in msg_list if msg])
        else:
            await send_forward_msg_group(bot, event, name=f'{Bot_NICKNAME}', msgs=[msg for msg in msg_list if msg])
    else:
        msg += "获取图片失败。"
        await setu.finish(msg, at_sender=True)


set_api = on_command("设置图库", aliases={"切换图库", "指定图库"}, priority=50, block=True)


@set_api.got(
    "api",
    prompt=(
            "请选择以下数字切换图库:\n"
            "1 : Xi_Lusheng API\n"
            "2 : Lolicon API"
    )
)
async def _(event: PrivateMessageEvent, api: Message = Arg()):
    api = str(api)
    user_id = str(event.user_id)
    if api == "1":
        customer_api[user_id] = "Xi_Lusheng API"
        save()
        await set_api.finish("图库已切换为Xi_Lusheng API")
    elif api == "2":
        customer_api[user_id] = "Lolicon API"
        save()
        await set_api.finish("图库已切换为Lolicon API")
    else:
        await set_api.finish("图库设置失败")

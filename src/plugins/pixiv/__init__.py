import asyncio
import re
import httpx
import requests
import unicodedata
from src.plugins.pixiv.url import Lolicon, Xi_Lusheng
from src.plugins.pixiv.utils import customer_api, save
from utils.config import Bot_NICKNAME
from utils.utils_def import send_forward_msg_group
from nonebot import on_regex, on_command, logger
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.internal.params import ArgPlainText, Arg
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import MessageSegment, MessageEvent
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State
from src.plugins.pixiv.constant import make_new_image, func

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


@setu.handle()
async def setu_(bot: Bot, event: MessageEvent):
    msg = ''
    data = None
    url_list = []
    new_list = []
    msg_list = []
    R18 = 0
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
    api = customer_api.get("url", None)
    get_r18 = customer_api.get("r18", False)

    if get_r18:
        if Tag.startswith("r18"):
            if api == "Xi_Lusheng API":
                R18 = 2
            elif api == "Lolicon API":
                Tag = Tag[3:]
                R18 = 1
        else:
            R18 = 0
    else:
        R18 = 0
        await setu.send(f"管理员关闭了r18功能哦，但是{Bot_NICKNAME}还是为你准备了非r18的涩图")

    try:
        if api == "Lolicon API":
            if Tag:
                msg, data = Lolicon(N, Tag, R18)
            else:
                msg, data = Lolicon(N, '', R18)
        elif api == "Xi_Lusheng API":
            if R18 == 2:
                msg, data = Xi_Lusheng(N, R18)
            else:
                msg, data = Xi_Lusheng(N, 1)

        for i in data:
            url_list.append(i['url'])

        msg += f"\n图片取自：{api}"

        await setu.send(msg, at_sender=True)

        async with httpx.AsyncClient() as client:
            task_list = []
            for urls in url_list:
                task = asyncio.create_task(func(client, urls))
                task_list.append(task)
            image_list = await asyncio.gather(*task_list)

        image_list = [image for image in image_list if image]

        if image_list:
            if api == "Xi_Lusheng API" and R18 == 0:
                pixiv = 'url'
            else:
                for i in range(len(image_list)):
                    image = await make_new_image(image_list[i])
                    new_list.append(image)
                data = [dict(d, **{'image': i}) for i, d in zip(new_list, data)]
                pixiv = 'image'

            for x in data:
                msg_list.append(MessageSegment.text("芝士幻影坦克：\n")
                                +
                                MessageSegment.image(x[pixiv])
                                +
                                MessageSegment.text(f"\n图片id：{x['pixiv_id']}\n"
                                                    f"图片链接：{x['url']}"))

            await send_forward_msg_group(bot, event, name=f'{Bot_NICKNAME}', msgs=[msg for msg in msg_list if msg])

        else:
            await setu.finish("获取图片失败。", at_sender=True)
    except Exception as e:
        logger.error("出现错误：" + str(e))
        await setu.finish("出现错误：" + str(e), at_sender=True)


set_api = on_regex("^(设置|切换|指定)图库$", permission=SUPERUSER, priority=50, block=True)


@set_api.got(
    "api",
    prompt=(
            "请选择以下数字切换图库:\n"
            "1 : Xi_Lusheng API (个人收藏用，不支持Tag筛选)\n"
            "2 : Lolicon API (他人图库，容易请求超时)"
    )
)
async def _(api: Message = Arg()):
    if str(api) == "1":
        name = "Xi_Lusheng API"
        customer_api["url"] = name
        save()
        await set_api.finish(f"图库已切换为{name}")
    elif str(api) == "2":
        name = "Lolicon API"
        customer_api["url"] = name
        save()
        await set_api.finish(f"图库已切换为{name}")
    else:
        await set_api.finish(f"图库设置失败")


set_r18 = on_regex("^(开启|关闭)r18$", permission=SUPERUSER, priority=50, block=True)


@set_r18.handle()
async def _(event: MessageEvent):
    r18 = event.get_plaintext()
    if r18[:2] == "开启":
        customer_api["r18"] = True
        save()
        await set_r18.finish(f"r18已{r18[:2]}")
    elif r18[:2] == "关闭":
        customer_api["r18"] = False
        save()
        await set_r18.finish(f"r18已{r18[:2]}")
    else:
        await set_r18.finish(f"r18设置失败")


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

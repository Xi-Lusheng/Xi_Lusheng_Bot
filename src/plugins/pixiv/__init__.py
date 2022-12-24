import base64
import re
import requests
from nonebot import on_regex, on_command
from nonebot.adapters import Message
from nonebot.internal.params import ArgPlainText
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.exception import ActionFailed
from nonebot.adapters.onebot.v11 import Event, MessageSegment
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State

from src.plugins.pixiv.constant import get_image, make_new_image

__plugin_meta__ = PluginMetadata(
    name='二次元',
    description='发送动漫图片',
    usage='',
    extra={
        'menu_data': [
            {
                'func': '二次元',
                'trigger_method': 'on_re',
                'trigger_condition': '二次元 来点二次元',
                'brief_des': '发送二次元图片',
                'detail_des': '发送二次元图片'
            },
            {
                'func': '涩图',
                'trigger_method': 'on_re',
                'trigger_condition': '涩图 来点涩图',
                'brief_des': '发送涩图',
                'detail_des': '发送涩图'
            },
            {
                'func': 'r18',
                'trigger_method': 'on_re',
                'trigger_condition': 'r18 来点r18',
                'brief_des': '发送r18幻影坦克图片',
                'detail_des': '发送r18幻影坦克图片'
            },
        ],
        'menu_template': 'default'
    }
)

pixiv = on_regex('^(二次元|涩图|色图|r18)$|^来点(二次元|涩图|色图|r18)$', block=True, priority=10)


@pixiv.handle()
async def pixiv_(event: Event):
    msg = event.get_plaintext()
    r18 = re.search('r18', msg)
    r16 = re.search('(涩图|色图)', msg)
    data = None
    if r18:
        await pixiv.send('请等待合成幻影坦克', at_sender=True)
        data = await get_image(sort=2)
    elif r16:
        await pixiv.send('请等待合成幻影坦克', at_sender=True)
        data = await get_image(sort=1)
    try:
        message = await make_new_image(data)
        image = MessageSegment.image(f"base64://{base64.b64encode(message['new_image'].getvalue()).decode()}")
        result = image + MessageSegment.text(f"\n图片id：{message['image_id']}\n"
                                             f"图片链接：{message['image_url']}")
        await pixiv.finish(result)
    except (ActionFailed, ValueError):
        await pixiv.send("合成失败将只发送原图链接")
        await pixiv.finish(MessageSegment.text(f"图片id：{data['image_id']}\n"
                                               f"图片链接：{data['image_url']}"))
    else:
        data = await get_image(sort=0)
        try:
            image = MessageSegment.image(data['image_url'])
            result = image + MessageSegment.text(f"\n图片id：{data['image_id']}\n"
                                                 f"图片链接：{data['image_url']}")
            await pixiv.finish(result)
        except ActionFailed:
            await pixiv.send("图片发送失败可能被风控，将合成幻影坦克")
            message = await make_new_image(data)
            image = MessageSegment.image(f"base64://{base64.b64encode(message['new_image'].getvalue()).decode()}")
            result = image + MessageSegment.text(f"\n图片id：{message['image_id']}\n"
                                                 f"图片链接：{message['image_url']}")
            await pixiv.finish(result)
        except ValueError:
            await pixiv.send("幻影坦克合成失败，将发送图片原链接")
            await pixiv.finish(MessageSegment.text(f"图片id：{data['image_id']}\n"
                                                   f"图片链接：{data['image_url']}"))


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

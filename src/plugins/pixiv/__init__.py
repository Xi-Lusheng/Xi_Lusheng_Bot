import base64
import re
import time

from nonebot import on_regex
from nonebot.adapters.onebot.exception import ActionFailed
from nonebot.adapters.onebot.v11 import Event, MessageSegment
from nonebot.plugin import PluginMetadata
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
    if r18:
        await pixiv.send('r18请等待合成幻影坦克', at_sender=True)
        data = await get_image(sort=2)
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
    elif r16:
        data = await get_image(sort=1)
    else:
        data = await get_image(sort=0)
    try:
        image = MessageSegment.image(data['image_url'])
        result = image + MessageSegment.text(f"图片id：{data['image_id']}")
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

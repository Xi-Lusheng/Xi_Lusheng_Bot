import base64
import io
import re

import requests
from nonebot import on_regex
from nonebot.adapters.onebot.v11 import Event, MessageSegment
from nonebot.plugin import PluginMetadata
from src.plugins.pixiv.constant import get_image, get_new_image, get_resize_image, color_car
from src.plugins.pixiv.create_data import create_file

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
                'brief_des': '发送动漫图片',
                'detail_des': '发送动漫图片'
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

create_file()
pixiv = on_regex(r'^二次元$|^来点二次元$|^r18$|^来点\s*r18$', block=True, priority=10)


@pixiv.handle()
async def pixiv_(event: Event):
    msg = event.get_plaintext()
    r18 = re.search('r18', msg)
    result = await get_image(msg)
    image_id = result['image_id']
    image = result['image']
    if r18:
        message = MessageSegment.text(f"\n图片id：{image_id}\n"
                                      f"图片链接：{image}")
        await pixiv.send(message, at_sender=True)
        await pixiv.send('查看r18请等待合成幻影坦克', at_sender=True)
        image_path = requests.get(image)
        img_on = await get_new_image()
        img_in = await get_resize_image(io.BytesIO(image_path.content))
        image = await color_car(img_on, img_in)
        await pixiv.finish(MessageSegment.image(f"base64://{base64.b64encode(image.getvalue()).decode()}"))
    else:
        res = MessageSegment.image(image)
        result = MessageSegment.text(f"图片id：{image_id}\n") + res
        await pixiv.finish(result)


setu = on_regex("^涩图$|^setu$|^无内鬼$|^色图$|^涩图tag.+$")


@setu.handle()
async def setu_():
    await setu.finish("涩图功能暂时关闭重新构建代码中")

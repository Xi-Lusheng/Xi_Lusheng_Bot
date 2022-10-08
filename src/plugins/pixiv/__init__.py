import re
from nonebot import on_regex
from nonebot.adapters.onebot.v11 import Event
from nonebot.plugin import PluginMetadata
from src.plugins.pixiv.constant import get_image
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
    if r18:
        await pixiv.send('查看r18请等待合成幻影坦克', at_sender=True)
    result = await get_image(msg)
    await pixiv.finish(result)


setu = on_regex("^涩图$|^setu$|^无内鬼$|^色图$|^涩图tag.+$")


@setu.handle()
async def setu_():
    await setu.finish("涩图功能暂时关闭重新构建代码中")

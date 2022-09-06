from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
import urllib3
import json
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name='d2',
    description='暂时维护中，勿用',
    usage='/',
    extra={
        'menu_data': [
            {
                'func': '日报',
                'trigger_method': 'on_cmd',
                'trigger_condition': '/日报',
                'brief_des': '查看d2日报命令',
                'detail_des': '暂时维护中，勿用'
            },
        ],
        'menu_template': 'default'
    }
)

today = on_command("today", aliases={'日报', }, priority=5)


@today.handle()
async def handle_first_receive(event: GroupMessageEvent, message: Message = CommandArg()):
    try:
        try:
            url = 'http://www.tianque.top/d2api/today/'

            r = urllib3.PoolManager().request('GET', url)
            hjson = json.loads(r.data.decode())

            img_url = hjson["img_url"]

            cq = "[CQ:image,file=" + img_url + ",id=40000]"

            await today.send(Message(cq))
        except:
            url = 'http://www.tianque.top/d2api/today/'

            r = urllib3.PoolManager().request('GET', url)
            hjson = json.loads(r.data.decode())

            error_url = hjson["error"]
            await today.send("获取日报失败\n" +
                             "error:\n" +
                             error_url)
    except:
        await today.send("获取日报失败:\n服务器错误")

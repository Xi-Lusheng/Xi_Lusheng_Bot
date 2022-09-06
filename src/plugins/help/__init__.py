from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name='机器人信息',
    description='了解机器人信息',
    usage='/',
    extra={
        'menu_data': [
            {
                'func': '机器人介绍',
                'trigger_method': 'on_cmd',
                'trigger_condition': '/info 或 /信息',
                'brief_des': '介绍机器人信息与代码架构',
                'detail_des': '介绍机器人信息与代码架构'
            },
        ],
        'menu_template': 'default'
    }
)

help_ = on_command('info', aliases={'信息'}, priority=1, block=True)


@help_.handle()
async def _(bot: Bot, event: Event):
    await help_.finish('欢迎使用汐鹿生制作的初号姬，发送 ‘菜单’ 查看机器人目前支持的功能\n'
                       '======================\n'
                       '此项目基于 Nonebot2 和 go-cqhttp 开发Q群机器人\n'
                       '实现了一些对群友的娱乐功能和实用功能（大概）\n'
                       '======================\n'
                       '项目地址：https://gitee.com/xi-lusheng/nonebot2\n'
                       'nonebot官方文档地址：https://v2.nonebot.dev/')

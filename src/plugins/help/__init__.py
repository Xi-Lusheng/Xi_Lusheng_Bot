from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Event

help_ = on_command('help', aliases={'帮助'}, priority=1, block=True)


@help_.handle()
async def _(bot: Bot, event: Event):
    await help_.finish('欢迎使用汐鹿生制作的初号姬，目前支持以下功能\n'
                       '=========================\n'
                       '命令类：\n'
                       '帮助文档： /help /帮助\n' + '查看初号姬命令\n'
                       '游戏王查卡：ygo <卡名>\n' + '查找指定卡片信息\n'
                       '=========================\n'
                       '指定类：\n'
                       '@初号姬 <remake/liferestart/人生重开/人生重来>\n' + '开始人生重开小游戏吧\n' +
                       '@初号姬 <任何内容>\n' + '和人工智能（智障）聊天\n'
                       '=========================\n'
                       '被动技能：\n'
                       '时不时胡言乱语\n' +
                       '谁还不是个复读姬呢？ （当群里开始+1时，初号姬也会参一脚）\n'
                       '更多技能正在开发中......\n'
                       '项目地址：https://gitee.com/xi-lusheng/nonebot2')

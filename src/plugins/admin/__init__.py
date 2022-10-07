from nonebot import on_regex
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from utils.config import Bot_NICKNAME, Bot_ID
from utils.permission import get_group_role
from nonebot.plugin import PluginMetadata
from utils.utils_def import GetRe

__plugin_meta__ = PluginMetadata(
    name='管理员插件',
    description='使用命令完成管理员功能',
    usage='/',
    extra={
        'menu_data': [
            {
                'func': '撤回消息',
                'trigger_method': 'on_re',
                'trigger_condition': '[回复选择需要撤回的信息] 撤回',
                'brief_des': '帮助没有管理员权限群友撤回消息',
                'detail_des': '帮助没有管理员权限群友撤回消息'
            },
        ],
        'menu_template': 'default'
    }
)

withdraw = on_regex("撤回$", priority=5, block=True)


@withdraw.handle()
async def withdraw_(bot: Bot, event: GroupMessageEvent):
    get_re = GetRe(event.raw_message)
    msg_id = (get_re.get_msg_id()).group(1)
    at_id = (get_re.get_at_id()).group(1)
    if msg_id and at_id:
        user_role = await get_group_role(bot, event, at_id)
        bot_role = await get_group_role(bot, event, Bot_ID)
        if bot_role == 'owner':
            await bot.delete_msg(message_id=msg_id)
            await withdraw.finish('已撤回')
        elif bot_role == 'admin':
            if user_role == bot_role and at_id != Bot_ID or user_role == 'owner':
                await withdraw.finish(f'{Bot_NICKNAME}没有足够的权限撤回ta的消息哦')
            else:
                await bot.delete_msg(message_id=msg_id)
                await bot.delete_msg(message_id=event.message_id)
                await withdraw.finish('已撤回')
        else:
            await withdraw.finish(f'{Bot_NICKNAME}没有足够权限哦，让群主大大给{Bot_NICKNAME}个管理员权限吧')
    else:
        await withdraw.finish('命令不规范，请先使用回复选择需要撤回的消息')



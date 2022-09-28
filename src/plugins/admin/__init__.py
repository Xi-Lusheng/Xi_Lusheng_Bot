import re

from nonebot import on_regex
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from utils.config import Bot_NICKNAME, Bot_ID, COMMAND_START, Bot_MASTER
from utils.permission import admin_permission, get_group_role
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
                'trigger_condition': '[回复选择需要撤回的信息] /撤回',
                'brief_des': '撤回消息',
                'detail_des': '撤回消息'
            },
            {
                'func': '全体禁言',
                'trigger_method': 'on_re',
                'trigger_condition': '/全体禁言 /关闭全体禁言',
                'brief_des': '打开或者关闭全体禁言',
                'detail_des': '打开或者关闭全体禁言'
            },
            {
                'func': '单人禁言',
                'trigger_method': 'on_re',
                'trigger_condition': '禁言@他 cd 或 @他 禁言cd',
                'brief_des': '@要禁言的 QQ 号，cd是禁言时间，0为解除禁言',
                'detail_des': '@要禁言的 QQ 号，cd是禁言时间，0为解除禁言'
            },
        ],
        'menu_template': 'default'
    }
)

withdraw = on_regex(f"({COMMAND_START}撤回)", priority=5, block=True)


@withdraw.handle()
async def withdraw_(bot: Bot, event: GroupMessageEvent):
    get_re = GetRe(event.raw_message)
    msg_id = (get_re.get_msg_id()).group(1)
    at_id = get_re.get_at_id()
    if msg_id and at_id:
        for id_ in at_id:
            user_role = await get_group_role(bot, event, id_.group())
            bot_role = await get_group_role(bot, event, Bot_ID)
            if bot_role == 'owner':
                await bot.delete_msg(message_id=msg_id)
                await withdraw.finish('已撤回')
            elif bot_role == 'admin':
                if user_role == bot_role and id_.group() != Bot_ID or user_role == 'owner':
                    await withdraw.finish(f'{Bot_NICKNAME}没有足够的权限撤回ta的消息哦')
                else:
                    await bot.delete_msg(message_id=msg_id)
                    await withdraw.finish('已撤回')
            else:
                if id_.group() == Bot_ID:
                    await bot.delete_msg(message_id=msg_id)
                else:
                    await withdraw.finish(f'{Bot_NICKNAME}没有足够权限哦，让群主大大给{Bot_NICKNAME}个管理员权限吧')
    else:
        await withdraw.finish('命令不规范，请先使用回复选择需要撤回的消息')


taboo_all = on_regex(f'^{COMMAND_START}(全体禁言|关闭全体禁言)$', priority=5, block=True)


@taboo_all.handle()
async def taboo_all_(bot: Bot, event: GroupMessageEvent):
    if await admin_permission(bot, event):
        enable = None
        if event.get_plaintext() == f'{COMMAND_START}全体禁言':
            enable = True
        elif event.get_plaintext() == f'{COMMAND_START}关闭全体禁言':
            enable = False
        await bot.set_group_whole_ban(group_id=int(event.group_id), enable=bool(enable))
    else:
        await taboo_all.finish('你没有权限使用这个命令哦', at_sender=True)


taboo = on_regex(r'^禁言\s*(\[CQ:at,qq=[1-9][0-9]{4,10}\])+\s*cd\d*$|^(\[CQ:at,qq=[1-9][0-9]{4,10}\])+\s*禁言\s*cd\d*$',
                 priority=5, block=True)


@taboo.handle()
async def taboo_(bot: Bot, event: GroupMessageEvent):
    if await admin_permission(bot, event):
        get_re = GetRe(event.raw_message)
        cd = (get_re.get_cd()).group(1)
        at_id = get_re.get_at_id()
        if at_id and cd:
            for id_ in at_id:
                user_role = await get_group_role(bot, event, id_.group())
                bot_role = await get_group_role(bot, event, Bot_ID)
                if bot_role == 'owner':
                    await bot.set_group_ban(group_id=event.group_id, user_id=id_.group(), duration=cd)
                elif bot_role == 'admin':
                    if user_role == bot_role and id_.group() != Bot_ID or user_role == 'owner':
                        await taboo.finish(f'{Bot_NICKNAME}没有足够的权限禁言ta哦')
                    elif id_.group() == Bot_ID:
                        await taboo.finish('你是猪比吗，你见过谁能自己禁言自己', at_sender=True)
                    elif id_.group() in bot.config.superusers:
                        await taboo.finish(f'不能禁言{Bot_MASTER}哦', at_sender=True)
                    else:
                        await bot.set_group_ban(group_id=event.group_id, user_id=id_.group(), duration=cd)
                else:
                    await taboo.finish(f'{Bot_NICKNAME}没有足够权限哦，让群主大大给{Bot_NICKNAME}个管理员权限吧')
    else:
        await taboo.finish('你没有权限使用这个命令哦', at_sender=True)


set_admin = on_regex(r'^(设置|取消)管理员\s*\[CQ:at,qq=[1-9][0-9]{4,10}\]$|^\[CQ:at,qq=[1-9][0-9]{4,10}\]\s*(设置|取消)管理员$',
                     block=True, priority=5)


@set_admin.handle()
async def set_admin_(bot: Bot, event: GroupMessageEvent):
    if await admin_permission(bot, event):
        get_re = GetRe(event.raw_message)
        at_id = (get_re.get_at_id()).group(1)
        msg = (re.search('(设置|取消)管理员', event.raw_message)).group(1)
        if at_id and msg:
            pass
    else:
        await set_admin.finish('你没有权限使用这个命令哦', at_sender=True)
